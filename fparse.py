import json
import logging

import yaml


class FractalParser:
    # NOTE: Effectively this is a fractal meta-parser that outsources its brain to `list_of_keys`.
    # A parser using recipes for parsing recipes...or any other data structure
    # With the right recipe, it can parse any data structure.
    # A list_of_keys for complex data structures can be built up step by step from simpler ones.
    # In extreme cases, you could dynamically generate `list_of_keys` at runtime to tackle
    # completely unknown formats.
    # The parser is a fractal meta-parser that can parse diverse data structures
    # Expected input is a json data structure and a yaml list of keys with keys and instructions
    # Valid instructions are:
    # key: the key to look for in the json data
    # addlevel: add a level to the header level
    # header: if true, this will be printed as a header
    # prepend: text to prepend
    # append: text to append
    # insert: text to insert
    # children: a list of keys to look for in the json data
    # separator: bool or text to insert as a separator
    # newlines: number of newlines to insert
    # printkey: if true, the key will be printed, not only the value
    # enumerate: if true, the index will be enumerated, this takes precedence over islist
    # islist: if true, the output will be a list
    #
    # Example:
    # list_of_keys = """
    # - key: meta_title
    #   addlevel: -1
    #   header: true
    # - key: meta_description
    #   append: "\\n"
    # - key: ingredients
    #   header: true
    #   children:
    #     - enumerate: true
    #     - islist: true # will be ignored if enumerate is true
    #     - key: amount
    #     - key: unit
    #     - key: ingredient
    #     - key: appendix
    #     - separator: true # this adds a separator after each child
    #   insert: "\\nthis is an insert\\n"
    #   append: "\\nthis is an append\\n"
    #   prepend: "\\nthis is a prepend\\n"
    #   """

    # WARNING: Here be dragons! This descent would make Escher blush and Mandelbrot smile.
    # DO NOT TOUCH - It's slightly complex - and a bit cursed.
    # Not spaghetti, fractal lasagna.
    # Pro: It works. Despite - not because!

    @staticmethod
    def _parse(
        json_data,
        list_of_keys,
        level=1,
        ignore_none=True,
        ignore_empty_list=True,
        ignore_list=True,
    ):
        md_parts = []
        if json_data is None:
            return md_parts
        if isinstance(json_data, list):
            for i, item in enumerate(json_data):
                all_keys = [key for key in list_of_keys]
                if any("enumerate" in key for key in list_of_keys):
                    md_parts.append(f"{i + 1}. ")
                elif any("islist" in key for key in list_of_keys):
                    md_parts.append("- ")
                parts_to_append = FractalParser._parse(
                    item, list_of_keys, level, ignore_none, ignore_empty_list
                )
                if parts_to_append != []:
                    md_parts.extend(parts_to_append)
                    if any(
                        k in key
                        for key in list_of_keys
                        for k in ["islist", "enumerate"]
                    ):
                        md_parts.append("\n")
            return md_parts

        if isinstance(list_of_keys, list):
            new_json_data = json_data

            for rules in list_of_keys:
                if "key" in rules:
                    key = rules["key"]
                    new_json_data = json_data.get(key)
                    new_rules = rules
                    new_level = level
                    if new_json_data is None or new_json_data == "None":
                        if ignore_none:
                            logging.debug(f"Ignoring None for key: {key}")
                            continue
                    if "addlevel" in new_rules:
                        new_level += new_rules["addlevel"]
                    if "header" in new_rules and new_rules["header"]:
                        newline = ""
                        if new_level > 1:
                            newline = "\n\n"
                        md_parts.append(newline)
                    if "prepend" in new_rules:
                        md_parts.append(new_rules["prepend"])
                    if len(new_rules) == 1 and "key" in new_rules:
                        if isinstance(new_json_data, (str, int, float, bool)):
                            md_parts.append(f"{new_json_data} ")
                            continue
                        elif new_json_data == []:
                            logging.debug(f"FOUND EMPTY LIST FOR KEY: {key}")
                            if ignore_empty_list:
                                logging.debug(f"Ignoring empty list for key: {key}")
                                continue
                        else:
                            if ignore_list:
                                logging.debug(f"LIST FOUND, IGNORING: {new_json_data}")
                                continue
                    if "header" in new_rules and new_rules["header"]:
                        if isinstance(new_json_data, (str, int, float, bool)):
                            md_parts.append(f"{'#' * new_level} {new_json_data}\n")
                        else:
                            # only simple types should be printed as headers, so we print the key
                            md_parts.append(f"{'#' * new_level} {new_rules['key']}\n")
                            if (
                                not ignore_list
                                and new_json_data != []
                                and "children" not in new_rules
                            ):
                                md_parts.append(f"{new_json_data}\n")
                    if "key" in new_rules and "header" not in new_rules:
                        if "printkey" in new_rules:
                            md_parts.append(f"{new_rules['key']}: ")
                        if isinstance(new_json_data, (str, int, float, bool)):
                            md_parts.append(f"{new_json_data}\n")
                        elif not ignore_empty_list and new_json_data == []:
                            md_parts.append(f"{new_json_data}\n")
                        elif not ignore_list:
                            md_parts.append(f"{new_json_data}\n")
                        elif "children" not in new_rules:
                            # NOTE: this should be unreachable, but it's here for safety
                            logging.warning(
                                f"WARNING: odd stuff happening: {new_json_data}\nKey: {key}\nRules: {rules}"
                            )

                    if "insert" in new_rules:
                        md_parts.append(new_rules["insert"])
                    if "children" in new_rules:
                        md_parts.extend(
                            FractalParser._parse(
                                new_json_data,
                                new_rules["children"],
                                new_level + 1,
                                ignore_none,
                                ignore_empty_list,
                            )
                        )
                    if "append" in new_rules:
                        # strip newlines from the end of the string
                        md_parts[-1] = md_parts[-1].rstrip("\n")
                        md_parts.append(new_rules["append"])
                    if "separator" in new_rules:
                        if new_rules["separator"] is True:
                            if (
                                "enumerate" not in new_rules
                                and "islist" not in new_rules
                            ):
                                md_parts.append("\n")
                            md_parts.append("---\n")
                        else:
                            md_parts.append(new_rules["separator"])
                    if "newlines" in new_rules:
                        md_parts.append("\n" * new_rules["newlines"])
                else:
                    if "newlines" in rules:
                        md_parts.append("\n" * rules["newlines"])
                    if "separator" in rules:
                        if rules["separator"] is True:
                            md_parts.append("\n\n---\n")
                        else:
                            md_parts.append(rules["separator"])
                    if "insert" in rules:
                        md_parts.append(rules["insert"])

        elif isinstance(list_of_keys, dict):
            logging.error(
                f"ERROR: list_of_keys is a dict but should be a list: {list_of_keys}"
            )
            raise ValueError(
                f"\033[91mERROR: list_of_keys is a dict but should be a list: {list_of_keys}\033[0m\n"
            )
        else:
            logging.error(
                f"\033[91mUnexpected type for list_of_keys: {type(list_of_keys)}\033[0m\n"
            )
            raise ValueError(
                f"\033[91mUnexpected type for list_of_keys: {type(list_of_keys)}\033[0m\n"
            )
        return md_parts

    @staticmethod
    def parse(
        json_data,
        list_of_keys,
        level=1,
        ignore_none=True,
        ignore_empty_list=True,
        ignore_list=True,
    ):
        try:
            list_of_keys = yaml.safe_load(list_of_keys)
        except Exception as e:
            logging.error(f"Error loading list_of_keys: {e}")
            raise ValueError(
                f"\033[91mERROR: Could not load list_of_keys: {e}\033[0m\n"
            )
        return FractalParser._parse(
            json_data,
            list_of_keys,
            level,
            ignore_none,
            ignore_empty_list,
            ignore_list,
        )


if __name__ == "__main__":
    input_file = "darkmatterbrownies.json"

    list_of_keys = """
- key: title
  header: true
  addlevel: -1  # Force top-level header
  newlines: 1

- key: description
  append: "\n\n"

- key: ingredients
  header: true
  prepend: "## "
  children:
    - enumerate: true
    - key: amount
      prepend: "**"
      append: "** "
    - key: unit
      append: " of "
    - key: ingredient
    - key: note
      prepend: " ("
      append: ")"
      separator: "\n"
  separator: "\n\n"

- key: steps
  header: true
  children:
    - key: preheat
      prepend: "🔥 "
    - key: mix
      children:
        - key: action
          prepend: "🌀 **Mixing:** "
        - key: tip
          prepend: "\n   💡 "
      separator: "\n"
    - key: bake
      children:
        - key: duration
          prepend: "⏳ **Bake:** "
        - key: note
          prepend: "\n NOTE: "
      separator: "\n"
    - key: expand
      prepend: "📈 "
  newlines: 2

- key: nutrition
  header: true
  children:
    - key: calories
      prepend: "📊 "
    - key: macronutrients
      prepend: "**Macronutrients:**\n\n"
      children:
        - key: carbs
          printkey: true
        - key: protein
          printkey: true
        - key: fat
          printkey: true
"""

    with open(input_file, "r") as f:
        json_data = json.load(f)
    parser = FractalParser()
    parsed_data = parser.parse(
        json_data,
        list_of_keys,
        level=2,
        ignore_none=True,
        ignore_empty_list=True,
        ignore_list=False,
    )
    parsed_data = "".join([str(elem) for elem in parsed_data])
    print("henlo")
    with open("output.md", "w") as f:
        f.write(parsed_data)
