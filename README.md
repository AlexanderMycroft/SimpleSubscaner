# crt.sh Subdomain Fetcher

A small, interactive Python tool that asks for a domain name, queries
`crt.sh`, and prints discovered subdomains to stdout. It normalizes the
input (strips scheme/path and handles IDNA) and removes wildcard entries.

## Features

- Interactive prompt for a domain
- Fetches subdomains from `crt.sh` via JSON output
- Normalizes domain input (scheme/path removal, IDNA support)
- Deduplicates and sorts results
- Spinner + status message while the request is running (stderr)

## Requirements

- Python 3.8+ (stdlib only; no external dependencies)
- Network access to `https://crt.sh/`

## Installation

Clone the repository and run the script directly:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
chmod +x crt_subdomains.py
```

## Usage

Run the script and enter a domain when prompted:

```bash
./crt_subdomains.py
```

Example session:

```text
Enter domain: example.com
Задача принята. Идет выполнение. |
dev.example.com
example.com
m.example.com
products.example.com
support.example.com
```

Output is printed to stdout, one subdomain per line, which makes it easy
to pipe into other tools:

```bash
./crt_subdomains.py | sort -u > subdomains.txt
```

## How It Works

The script calls:

```
https://crt.sh/?q=%.<domain>&output=json
```

Then it parses `name_value` fields, splits multiline entries, removes
wildcards (`*.example.com`), and filters out unrelated names.

## Notes and Limitations

- `crt.sh` may rate-limit or return HTTP 503 during high load.
  The script retries a few times with a short backoff.
- Results are based on certificate transparency logs, so missing or
  stale data is possible.
- The spinner uses stderr, while results go to stdout.

## Contributing

Issues and pull requests are welcome. If you propose a change, please
include a short rationale and test steps.

## License

MIT. See `LICENSE`.
