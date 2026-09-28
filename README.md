# pullYotoFiles

Downloads the audio tracks from a Yoto card share link (`https://share.yoto.co/s/...`) and saves them locally, organized by author and card title.

## How it works

1. Fetches the share page and pulls out the embedded `__NEXT_DATA__` JSON, which holds the card's chapter and track list.
2. Scrapes the card title (`card-title`) and author (`card-author`) from the page HTML.
3. Streams each audio track to disk in 8 KB chunks.

## Requirements

- Python 3.7+
- [`requests`](https://pypi.org/project/requests/)

```bash
pip install requests
```

## Configuration

The output location is hardcoded near the top of the script:

```python
output_dir = '/path/to/save/location'
```

Change this to wherever you want files saved.

## Usage

```bash
python pullYotoFiles.py <share_url> [author]
```

| Argument    | Required | Description |
|-------------|----------|-------------|
| `share_url` | Yes      | The Yoto card share link. |
| `author`    | No       | Overrides the author name scraped from the page. |

### Examples

```bash
# Use the author name from the page
python pullYotoFiles.py https://share.yoto.co/s/abc123

# Set the author yourself
python pullYotoFiles.py https://share.yoto.co/s/123abc "Roald Dahl"
```

### Author handling

- If you pass an author, it is always used.
- If you don't, the scraped author is used only when it's under 50 characters. A longer value usually means the scrape picked up the wrong HTML, so it's rejected.
- If no usable author is found, the script exits and asks you to pass one.

## Output

```
<output_dir>/
└── <Author>/
    └── <Card Title>/
        ├── 01-Chapter One.ogg
        ├── 02-Chapter Two.ogg
        └── ...
```

- Filenames are `<track key>-<track title>.<ext>`.
- Titles are sanitized to letters, digits, spaces, `_` and `-`.
- Existing files with the same name are overwritten.

## Supported formats

| Track format | Saved as |
|--------------|----------|
| `opus`       | `.ogg`   |
| `aac`        | `.ogg`   |

Any other format raises a `KeyError`. To support it, add an entry to the `file_format` dict.

## Known limitations

- **Page scraping is fragile.** The script depends on Yoto's current page markup and the `props.pageProps.card.content.chapters` JSON path. If Yoto changes the site, parsing will break.
- **AAC is saved with an `.ogg` extension.** AAC audio usually belongs in `.m4a`/`.aac`, so some players may not open these files. Changing `'aac': 'ogg'` to `'aac': 'm4a'` is probably more correct.
- **Card author isn't sanitized.** An author name containing `/` or other path characters could produce unexpected folders.
- **No retries or resume.** A failed request stops the whole run.
- **Only supports V1 cards** V2 cards have a different authentication method to access the files which this script does not handle.

## Note

Only use this with cards you own or have the right to download, and keep the files for backup usage only.
