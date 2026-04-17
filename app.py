# Written by: Mohamed El-Sayyad
# Download videos from almost all platforms
# Date: 1447/10/29 (Shawwal)

import yt_dlp
import sys

def list_formats(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    formats = info.get('formats', []) or []
    rows = []
    for f in formats:
        label = f.get('format_note') or f.get('format') or f.get('format_id') or ''
        height = f.get('height') or ''
        ext = f.get('ext') or ''
        acodec = f.get('acodec') or ''
        vcodec = f.get('vcodec') or ''
        tbr = f.get('tbr') or ''
        filesize = f.get('filesize') or f.get('filesize_approx') or ''
        rows.append({
            'format_id': f.get('format_id'),
            'label': label,
            'height': height,
            'ext': ext,
            'vcodec': vcodec,
            'acodec': acodec,
            'tbr': tbr,
            'filesize': filesize,
        })
    # sort by height then bitrate
    rows.sort(key=lambda x: (x['height'] or 0, x['tbr'] or 0))
    return info.get('title', 'unknown_title'), rows

def print_formats_table(formats):
    print("\nAvailable formats:")
    print(f"{'id':8} {'label':20} {'res':6} {'vcodec':10} {'acodec':10} {'tbr':6} {'size':10}")
    print("-"*80)
    for f in formats:
        size = f['filesize'] or ''
        if isinstance(size, int):
            try:
                size = f"{size/1024/1024:.2f}MB"
            except:
                size = str(size)
        print(f"{str(f['format_id']):8} {str(f['label'])[:20]:20} {str(f['height']):6} {str(f['vcodec'])[:10]:10} {str(f['acodec'])[:10]:10} {str(f['tbr'])[:6]:6} {size:10}")

def choose_format_interactive(formats):
    print("\nChoose a format id to download, or type 'best'/'worst':")
    choice = input("-> ").strip()
    if choice.lower() in ('best','worst'):
        return choice.lower()
    return choice

def build_ydl_opts(choice, formats, title):
    opts = {
        'quiet': False,
        'noplaylist': True,
        'outtmpl': '%(title)s.%(ext)s'
    }
    if choice in ('best','worst'):
        opts['format'] = 'best' if choice == 'best' else 'worst'
    else:
        # choice can be a format id or a combination like "137+140"
        opts['format'] = choice
    return opts

def main():
    try:
        print("""
▗▖  ▗▖   ▐▌ ▄▄▄  ▄   ▄ ▄▄▄▄  
▐▛▚▖▐▌   ▐▌█   █ █ ▄ █ █   █ 
▐▌ ▝▜▌▗▞▀▜▌▀▄▄▄▀ █▄█▄█ █   █ 
▐▌  ▐▌▝▚▄▟▌                  
""")
        print("[!] > Don't use this app/site for anything harmful or 18+ >")
        user_url = input("[*] Please enter your URL -> ").strip()
        if not user_url:
            return print("[!] Failed to get URL")

        title, formats = list_formats(user_url)
        print(f"\nTitle: {title}")
        print_formats_table(formats)

        choice = choose_format_interactive(formats)
        ydl_opts = build_ydl_opts(choice, formats, title)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([user_url])

    except Exception as e:
        return print(f"Error: {e}")

if __name__ == '__main__':
    main()
