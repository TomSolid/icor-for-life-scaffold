# Brand

The myICOR infinity mark, for branding the tools around the scaffold.

- `myicor-app-icon-ink.png` - orange mark on ink (dark), 800px square
- `myicor-app-icon-paper.png` - light variant
- `myicor-mark-ink.svg` / `myicor-mark-paper.svg` - vector marks

## Obsidian custom app icon

Set via Settings -> Appearance -> Custom app icon -> Choose, picking
`myicor-app-icon-ink.png`. Obsidian copies the image to its app config
as `~/Library/Application Support/obsidian/icon.png` (macOS). Two facts
worth knowing:

1. The icon is APP-GLOBAL: it brands every vault on the machine, not
   just this one.
2. Automating it on a new machine is one file copy to that path (then
   restart Obsidian); the picker is only needed the first time.
