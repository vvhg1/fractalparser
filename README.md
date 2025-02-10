# FractalParser: The Recursive Meta-Parser

*Turn nested JSON into Markdown with the elegance of recursion, the precision of YAML, and just enough chaos to keep things interesting.*  

---

## **Concept**  

The **FractalParser** is a recursive meta-parser that transforms JSON/YAML data into structured Markdown using a customizable "recipe" (`list_of_keys`). Think of it as **Swiss Army knife meets Inception**:  

- **Self-Similar Logic**: Parses nested data structures by recursively invoking itself, mirroring the fractal nature of your data.  
- **Declarative Control**: Define parsing rules in YAML (the `list_of_keys`) to craft headers, lists, separators, and annotations—no code changes needed.  
- **Context-Aware**: Automatically adjusts Markdown header levels and handles empty/null values like a tactful diplomat.  

*Warning: May occasionally generate output that questions the meaning of existence. Keep logging enabled for existential crises.*  

---

## **The `list_of_keys` Grimoire 📖**  

A YAML list of instructions to bend the parser to your will. Each key is a directive that shapes the output:  

### **Core Incantations**  

| Key               | Effect                                                                 | Default | Example                          |  
|-------------------|-----------------------------------------------------------------------|---------|----------------------------------|  
| `key`             | JSON key to extract. If omitted, processes current level.            | –       | `key: meta_title`                 |
| `header`          | Renders value as a Markdown header (level auto-increments).           | `false` | `header: true`                   |  
| `addlevel`        | Adjust header depth. See advanced usage for example.                  | `0`     | `addlevel: -1`                   |  
| `prepend`         | Text to insert **before** the value.                                  | –       | `prepend: "**Ingredient:** "`    |  
| `append`          | Text to insert **after** the value.                                   | –       | `append: "\\n"`                  |  
| `insert`          | Static text injected after value but before nested data.              | –       | `insert: "\n---\n"`              |  
| `children`        | Nested list of keys to process recursively.                           | –       | `children: [{key: amount}, ...]` |  
| `separator`       | Adds a separator (`---` if `true`, custom string otherwise).          | `false` | `separator: "✨"`                 |  
| `newlines`        | Inserts *n* newlines.                                                 | `0`     | `newlines: 2`                    |  
| `printkey`        | Prints the key alongside the value (e.g., `Difficulty: Hard`).        | `false` | `printkey: true`                 |  
| `enumerate`       | Renders list items as `1. ...` (overrides `islist`).                  | `false` | `enumerate: true`                |  
| `islist`          | Renders list items as `- ...` (unless `enumerate` is active).         | `false` | `islist: true`                   |  

### **Execution Order**  
1. `prepend` → `header` → `key/value` → `insert` → `children` → `separator` → `append` → `newlines`  
2. `enumerate` takes precedence over `islist`.  
3. Rules without `key` (e.g., `separator`) execute once per parent level.  

---

## **Ritual Examples**  

### **Example 1: Recipe to Markdown**  
**Input JSON**  
```json  
{
  "title": "Black Hole Brownies",
  "description": "A dessert so dense, it generates its own gravitational field. Handle with care.",
  "ingredients": [
    {
      "amount": 3,
      "unit": "kg",
      "ingredient": "dark matter",
      "note": "freshly collapsed"
    },
    {
      "amount": 1,
      "unit": "singularity",
      "ingredient": "cocoa"
    },
    {
      "amount": "n",
      "unit": "self-similarity",
      "ingredient": "fractal nightmares",
      "note": "where n ≥ ∞"
    }
  ],
  "steps": {
    "preheat": "Heat the universe to 10^32 K",
    "mix": {
      "action": "Stir until spacetime curvature forms swirls",
      "tip": "Use clockwise rotation to avoid anticausal effects"
    },
    "bake": {
      "duration": "12 aeons",
      "note": "Check periodically for quantum tunneling"
    },
    "expand": "Watch as the recipe grows in complexity"
  },
  "nutrition": {
    "calories": "≈∞ kcal",
    "macronutrients": {
      "carbs": "42g",
      "protein": "0g (it's theoretical)",
      "fat": "∞g (dark energy infused)"
    }
  }
}
```

**YAML Spell (list_of_keys)**

```yaml
- key: title
  header: true
  addlevel: -1  # Force top-level header, set to 2 in the call (2-1=1)!
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
```
## Output Markdown

```markdown
# Black Hole Brownies

A dessert so dense, it generates its own gravitational field. Handle with care.


## ## ingredients
1. **3** kg of dark matter  (freshly collapsed) 
2. **1** singularity of cocoa 
3. **n** self-similarity of fractal nightmares  (where n ≥ ∞) 



## steps
🔥 Heat the universe to 10^32 K
🌀 **Mixing:** Stir until spacetime curvature forms swirls
 💡 Use clockwise rotation to avoid anticausal effects
 ⏳ **Bake:** 12 aeons
 NOTE: Check periodically for quantum tunneling
 📈 Watch as the recipe grows in complexity




## nutrition
📊 ≈∞ kcal
**Macronutrients:**
carbs: 42g
protein: 0g (it's theoretical)
fat: ∞g (dark energy infused)
```


## Advanced Configuration

## Parser Parameters

| Argument             | Effect                                                                 |
|----------------------|-----------------------------------------------------------------------|
| `ignore_none`        | Skips `null` values in JSON data (default: `true`).                   |
| `ignore_empty_list`  | Skips empty lists (`[]`) in JSON data (default: `true`).              |
| `ignore_list`        | Skips non-empty lists as values. Set to false for discovery. (default: `true`). |

## Error Handling

Invalid YAML: Fails loudly with a ValueError (to assert dominance).
Unexpected YAML Structure: Raises a ValueError (to maintain order).
Missing Keys: Logs a warning but proceeds (like a forgiving deity).

## Installation & Usage

Summon Dependencies:
`pip install PyYAML`

## Basic Invocation:

```python
from FractalParser import FractalParser  

# Load your JSON data and YAML spellbook  
with open("ritual.json") as f:  
    json_data = json.load(f)  
with open("spellbook.yaml") as f:  
    list_of_keys = f.read()  

# Perform the ritual  
markdown_output = FractalParser.parse(  
    json_data,  
    list_of_keys,  
    level=2,              # Starting header depth  
    ignore_none=True,     # Silence the void  
    ignore_list=False     # Embrace the chaos  
)  

# Save the results (before they escape)  
with open("output.md", "w") as f:  
    f.write("".join(markdown_output))  
```

## Debugging:
DON'T.
If you must, enable logging:

    import logging  
    logging.basicConfig(level=logging.DEBUG)  # Reveal the parser's secrets  


## FAQ (Frequently Arcanely Queried)

❓ Why does my Markdown have unexpected headers?

    Check addlevel and parent header rules. Recursion doesn’t forgive.

❓ Can I parse XML/CSV/TOML?

    Convert them to JSON first. The parser considers other formats "mundane."

❓ How to handle large datasets?

    Sacrifice RAM to the recursion gods. Alternatively, optimize your list_of_keys.

❓ Why YAML instead of JSON for list_of_keys?

    YAML’s readability offsets the parser’s inherent chaos. Also, comments.

## Contribution Guidelines

    Code: PRs must include:

        Tests that pass under a blood moon.

        A haiku describing your change.

    Spells: New list_of_keys features must:

        Avoid summoning parser recursion demons.

        Include an example in /examples/examples/examples/examples.

    Issues: Describe:

        The incantation used.

        The expected vs. actual output.

        Any relevant runes (logs).

Powered by recursion, YAML, and the lingering fear that the parser understands more than we do.
