# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from dataclasses import dataclass
from io import BytesIO
import tempfile

from flask import current_app
import symbolic


@dataclass
class Module:
    debug_filename: str
    debug_id: str
    symcache: any


class Symbolicator:
    """Takes a downloader and a cache manager and symbolicates stacks."""
    def __init__(self, downloader, cachemanager):
        self.downloader = downloader
        self.cachemanager = cachemanager

    def download_sym_and_parse(self, debug_filename, debug_id):
        """Download and parse a symbol file.

        :param debug_filename: the debug filename; eg "xul.pdb"
        :param debug_id: the debug id; eg "5F84ACF1D63667F44C4C44205044422E1"

        :returns: symcache or None

        """
        if debug_filename.endswith(".pdb"):
            filename = debug_filename[:-4] + ".sym"
        else:
            filename = debug_filename + ".sym"
        data = self.downloader.get(debug_filename, debug_id, filename)
        if data is None:
            return None

        ndebug_id = symbolic.normalize_debug_id(debug_id)
        # FIXME(willkg): This should probably close the temp file before
        # symbolic parses it. Also, the temp directory should be configurable.
        with tempfile.NamedTemporaryFile(suffix=".sym") as fp:
            fp.write(data)
            fp.flush()
            current_app.logger.debug(
                "Creating temp file %s %s %s %s" % (
                    debug_filename, debug_id, filename, fp.name
                )
            )
            archive = symbolic.Archive.open(fp.name)
            obj = archive.get_object(debug_id=ndebug_id)
            symcache = obj.make_symcache()

        return symcache

    def get_symcaches(self, modules, modules_to_lookup):
        """Retrieves symcaches for list of modules.

        This will use the cachemanager and downloader to get symcaches for all
        the modules where available.

        :param modules: list of [debug_filename, debug_id]
        :param modules_to_lookup: list of module indexes to look up

        :returns: list of Module instances

        """
        # Modules is a list of [debug_filename, debug_id]
        modules_with_symcache = []
        for module_index, module in enumerate(modules):
            debug_filename, debug_id = module
            symcache = None

            if module_index in modules_to_lookup:
                cache_key = "%s/%s" % (debug_filename, debug_id.upper())
                try:
                    data = self.cachemanager.get(cache_key)
                    symcache = symbolic.SymCache.from_bytes(data)
                except KeyError:
                    symcache = self.download_sym_and_parse(debug_filename, debug_id)
                    if symcache is not None:
                        data = BytesIO()
                        symcache.dump_into(data)
                        self.cachemanager.set(cache_key, data.getvalue())

            modules_with_symcache.append(
                Module(
                    debug_filename=debug_filename,
                    debug_id=debug_id,
                    symcache=symcache
                )
            )

        return modules_with_symcache

    def symbolicate(self, stacks, modules):
        """Takes stacks and modules and returns symbolicated stacks.

        :param stacks: list of stacks of the form (module index, module offset)
        :param modules: list of (debug_filename, debug_id)

        :returns: dict with "stacks" and "known_modules" keys

        """
        # Figure out which modules we're going to use
        modules_to_use = set()
        for stack in stacks:
            for module_index, module_offset in stack:
                modules_to_use.add(module_index)

        # Get symcaches for modules we need to use and convert to Modules
        module_symcaches = self.get_symcaches(modules, modules_to_lookup=modules_to_use)

        found_modules = {
            "%s/%s" % (module.debug_filename, module.debug_id): (True if module.symcache else None)  # noqa
            for module in module_symcaches
        }
        symbolicated_stacks = []
        for stack in stacks:
            symbolicated_stack = []
            for frame_index, frame in enumerate(stack):
                module_index, module_offset = frame
                module = None
                data = {
                    "frame": frame_index,
                    "module": "<unknown>",
                    "module_offset": hex(module_offset),
                }

                if module_index != -1:
                    module = module_symcaches[module_index]
                    data["module"] = module.debug_filename

                    if module_offset != -1 and module.symcache is not None:
                        lineinfo = module.symcache.lookup(module_offset)
                        if lineinfo:
                            # FIXME(willkg): not sure why lookup returns a list,
                            # but grab the first line if there is one
                            lineinfo = lineinfo[0]

                            data["function"] = lineinfo.symbol
                            data["function_offset"] = hex(
                                module_offset - lineinfo.sym_addr
                            )
                            data["line"] = lineinfo.line

                symbolicated_stack.append(data)

            symbolicated_stacks.append(symbolicated_stack)

        # Return symbolicated stack
        return {
            "stacks": symbolicated_stacks,
            "found_modules": found_modules,
        }
