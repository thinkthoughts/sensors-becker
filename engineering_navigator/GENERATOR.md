# Engineering Navigator Generator

`tools/generate_engineering_navigator.py` generates each Engineering Driver's
`index.md` from its canonical `specification.yaml`.

## Preview changes

```bash
python3 tools/generate_engineering_navigator.py
```

## Generate all driver pages

```bash
python3 tools/generate_engineering_navigator.py --write
```

The first time you replace the manually authored absorber page, use:

```bash
python3 tools/generate_engineering_navigator.py \
  --driver absorber_manufacturing \
  --write \
  --force
```

After that page contains the generator marker, ordinary `--write` runs update
it without `--force`.

## Generate one driver

```bash
python3 tools/generate_engineering_navigator.py \
  --driver absorber_manufacturing \
  --write
```

## Check generated pages

```bash
python3 tools/generate_engineering_navigator.py --check
```

Exit codes:

- `0`: all requested pages are current
- `1`: one or more pages are missing or outdated
- `2`: specification or invocation error

## Canonical-source rule

Edit:

```text
engineering_navigator/<driver>/specification.yaml
```

Then regenerate `index.md`. Do not hand-edit a generated `index.md`.
