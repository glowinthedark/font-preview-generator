#!/usr/bin/env python3
"""
Font Specimen Generator (Aggregated Formats)
-------------------------------------------
Recursively scans for .ttf, .otf, .woff, and .woff2 files. De-duplicates matching 
font designs by family name, rendering a single preview block while mapping 
all available source file formats together inside the metadata block.
"""

import sys
import argparse
import html
import os
import webbrowser
from collections import defaultdict
from pathlib import Path

# Explicitly capture missing external dependencies with clear setup paths
try:
    from fontTools.ttLib import TTFont
except ImportError:
    print("[-] Error: Required dependency 'fonttools' is missing.", file=sys.stderr)
    print("    To resolve this issue, please install it using your preferred manager:\n", file=sys.stderr)
    print("    Using uv (recommended):", file=sys.stderr)
    print("        uv add fonttools brotli", file=sys.stderr)
    print("\n    Using pip fallback:", file=sys.stderr)
    print("        pip install fonttools brotli\n", file=sys.stderr)
    sys.exit(1)


def get_font_family_name(font_path: Path) -> str:
    """
    Extracts the true font family name from font metadata blocks.
    Falls back gracefully to the file stem name if parsing fails (e.g., if brotli 
    is missing for compressed .woff2 parsing).
    """
    try:
        # Open font file lazily to minimize memory overhead
        font = TTFont(font_path, fontNumber=0, lazy=True)
        name_table = font.get('name')
        if not name_table:
            return font_path.stem
            
        # Preferred Family (ID 16) is prioritized over Font Family Name (ID 1)
        for name_id in (16, 1):
            for record in name_table.names:
                if record.nameId == name_id:
                    try:
                        name_str = record.toUnicode().strip()
                        if name_str:
                            return name_str
                    except Exception:
                        continue
        return font_path.stem
    except Exception:
        # Secure fallback context across un-parseable variants
        return font_path.stem


def main():
    parser = argparse.ArgumentParser(
        description="Generate an aggregated typography specimen preview page for local fonts."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=".",
        help="Target folder path to scan recursively (default: current directory)."
    )
    parser.add_argument(
        "-t", "--text",
        default="""The quick brown fox jumps over the lazy dog.
天地玄黄，宇宙洪荒。日月盈仄，辰宿列张。寒来暑往，秋收冬藏。
ABCDEFGHIJKLMNOPQRSTUVWXYZ
abcdefghijklmnopqrstuvwxyz
1234567890
&!?@#$ €£¥ ©® .,:;'" ()[] {} <>""",
        help="Custom sample preview text string."
    )
    args = parser.parse_args()

    base_dir = Path(args.folder).resolve()
    if not base_dir.is_dir():
        print(f"[-] Error: Target path '{base_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Scanning '{base_dir}' recursively for web-compatible font targets...")
    
    # Expanded discovery scope across standard cross-platform assets
    font_extensions = {'.ttf', '.otf', '.woff', '.woff2'}
    found_files = sorted({
        p for p in base_dir.rglob('*') if p.suffix.lower() in font_extensions
    })

    if not found_files:
        print(f"[-] No valid font assets (.ttf, .otf, .woff, .woff2) found inside '{base_dir}'.")
        sys.exit(0)

    # Sort files into structural buckets based on font family context blocks
    font_groups = defaultdict(list)
    for path in found_files:
        family_name = get_font_family_name(path)
        font_groups[family_name].append(path)

    print(f"[+] Discovered {len(found_files)} files mapping to {len(font_groups)} unique font families.")

    font_faces_css = []
    font_cards_html = []
    output_html_file = Path.cwd() / "preview.html"

    preview_text = html.escape(args.text).replace('\n', '<br>')

    # Strategy index map to prefer compressed variants for browser rendering
    format_priority = {'.woff2': 0, '.woff': 1, '.ttf': 2, '.otf': 3}
    format_css_names = {
        '.ttf': 'truetype',
        '.otf': 'opentype',
        '.woff': 'woff',
        '.woff2': 'woff2'
    }

    for idx, (family_name, paths) in enumerate(font_groups.items()):
        font_id = f"specimen_font_{idx}"
        
        # Select the single optimal format engine asset to run the browser canvas preview
        sorted_paths = sorted(paths, key=lambda p: format_priority.get(p.suffix.lower(), 4))
        primary_path = sorted_paths[0]
        
        try:
            rel_path = os.path.relpath(primary_path, Path.cwd())
            web_path = Path(rel_path).as_posix()
        except ValueError:
            web_path = primary_path.as_uri()

        font_format = format_css_names.get(primary_path.suffix.lower(), 'truetype')
        
        # Inject structural @font-face style rule for processing asset rendering
        font_faces_css.append(f"""
        @font-face {{
            font-family: '{font_id}';
            src: url('{html.escape(web_path)}') format('{font_format}');
            font-weight: normal;
            font-style: normal;
            font-display: swap;
        }}""")

        # Aggregate the matching sibling filename tags into layout components
        filename_elements = ""
        for p in sorted(paths, key=lambda x: x.name):
            filename_elements += f'<code class="font-filename">{html.escape(p.name)}</code>'

        # Generate responsive sizing rows using Golden Scale ratios
        target_sizes = ["8pt", "12pt", "16pt", "26pt"]
        preview_rows = ""
        for size in target_sizes:
            preview_rows += f"""
            <div class="preview-row">
                <span class="size-tag">{size}</span>
                <p class="sample-display" style="font-family: '{font_id}', sans-serif; font-size: {size};">
                    {preview_text}
                </p>
            </div>"""

        font_cards_html.append(f"""
        <section class="font-card">
            <div class="card-meta">
                <h2 class="font-name">{html.escape(family_name)}</h2>
                <div class="filename-container">
                    {filename_elements}
                </div>
            </div>
            <div class="card-display-matrix">
                {preview_rows}
            </div>
        </section>""")

    # Unified UI framework with structural grid systems using the golden ratio
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Font Typography Specimen Sheet</title>
    <style>
        :root {{
            --phi: 1.61803398875;
            --base-unit: 1rem;
            
            /* Sacred Geometry Proportional Spacing Scale */
            --space-xs: calc(var(--base-unit) / var(--phi));            /* ~0.618rem */
            --space-sm: var(--base-unit);                              /* 1.000rem */
            --space-md: calc(var(--base-unit) * var(--phi));           /* ~1.618rem */
            --space-lg: calc(var(--base-unit) * var(--phi) * var(--phi)); /* ~2.618rem */
            --space-xl: calc(var(--base-unit) * var(--phi) * var(--phi) * var(--phi)); /* ~4.236rem */
            
            /* Structural Constraints */
            --max-width: calc(42.36rem * var(--phi)); /* Optimal reading containment ~68.54rem */
            --radius: calc(0.382rem * var(--phi));   /* Rounded component standard ~0.618rem */
            
            /* Sophisticated Editorial Colorways */
            --bg-canvas: #fbfbfc;
            --bg-surface: #ffffff;
            --text-primary: #111215;
            --text-secondary: #5d626e;
            --text-dimmed: #9499a6;
            --border-color: #ededf0;
            --accent-glow: rgba(42, 102, 255, 0.03);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-canvas);
            color: var(--text-primary);
            line-height: var(--phi);
            padding: var(--space-xl) var(--space-md);
            display: flex;
            flex-direction: column;
            align-items: center;
            -webkit-font-smoothing: antialiased;
        }}

        .container {{
            width: 100%;
            max-width: var(--max-width);
        }}

        header {{
            margin-bottom: var(--space-xl);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: var(--space-lg);
        }}

        h1 {{
            font-size: var(--space-lg);
            font-weight: 300;
            letter-spacing: -0.03em;
            color: var(--text-primary);
            margin-bottom: var(--space-xs);
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: var(--space-sm);
        }}

        .catalog-summary {{
            font-weight: 600;
            color: var(--text-primary);
        }}

        /* Dynamic Font Injection Site */
        {"".join(font_faces_css)}

        /* Component Framework */
        .font-card {{
            background-color: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: var(--radius);
            padding: var(--space-lg);
            margin-bottom: var(--space-lg);
            box-shadow: 0 calc(var(--space-xs) / 2) var(--space-md) rgba(0, 0, 0, 0.01);
            transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        .font-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 var(--space-md) var(--space-lg) rgba(0, 0, 0, 0.03);
            background-color: var(--accent-glow);
        }}

        .card-meta {{
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: var(--space-sm);
            margin-bottom: var(--space-md);
            gap: var(--space-sm);
        }}

        .font-name {{
            font-size: calc(1rem * var(--phi));
            font-weight: 600;
            letter-spacing: -0.01em;
        }}

        .filename-container {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: calc(var(--space-xs) / 2);
        }}

        .font-filename {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.8rem;
            color: var(--text-secondary);
            background: var(--bg-canvas);
            padding: calc(var(--space-xs) / 3) var(--space-xs);
            border-radius: calc(var(--radius) / 2);
            border: 1px solid var(--border-color);
            white-space: nowrap;
        }}

        .card-display-matrix {{
            display: flex;
            flex-direction: column;
            gap: var(--space-md);
        }}

        .preview-row {{
            display: flex;
            align-items: flex-start;
            gap: var(--space-md);
        }}

        .size-tag {{
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.75rem;
            color: var(--text-dimmed);
            width: var(--space-xl);
            flex-shrink: 0;
            padding-top: calc(var(--space-xs) / 2);
            user-select: none;
        }}

        .sample-display {{
            color: var(--text-primary);
            word-break: break-all;
            width: 100%;
        }}

        @media (max-width: 640px) {{
            .card-meta {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .filename-container {{
                align-items: flex-start;
                width: 100%;
            }}
            .font-filename {{
                width: 100%;
                overflow-x: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Typography Specimen</h1>
            <p class="subtitle">Discovered <span class="catalog-summary">{len(found_files)} source files</span> mapping to <span class="catalog-summary">{len(font_groups)} unified structural font designs</span>.</p>
        </header>
        <main>
            {"".join(font_cards_html)}
        </main>
    </div>
</body>
</html>
"""

    # Save output to disk
    output_html_file.write_text(html_content, encoding="utf-8")
    print(f"[+] Specimen file compiled successfully -> {output_html_file}")

    # Launch platform's default web browser window to view the asset directly
    print("[+] Launching system viewport configuration browser...")
    webbrowser.open(output_html_file.absolute().as_uri())


if __name__ == "__main__":
    main()
