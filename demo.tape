# peasy-document — Document Conversion Library Demo
Output demo.gif

Set FontSize 20
Set Width 1000
Set Height 580
Set Shell "zsh"
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set Padding 24

Type "uv run --with peasy-document python3"
Enter
Sleep 2.5s

Type "from peasy_document import markdown_to_html, csv_to_json, html_to_markdown"
Enter
Sleep 1s

Type "# Markdown to HTML"
Enter
Sleep 0.5s

Type "result = markdown_to_html('# Hello\\n\\nThis is **bold** text.')"
Enter
Sleep 1.5s

Type "print(result.content)"
Enter
Sleep 2s

Type "# CSV to JSON"
Enter
Sleep 0.5s

Type "result = csv_to_json('name,age\\nAlice,30\\nBob,25')"
Enter
Sleep 1.5s

Type "print(result.content)"
Enter
Sleep 2s

Type "# HTML to Markdown"
Enter
Sleep 0.5s

Type "result = html_to_markdown('<h1>Title</h1><p>A <strong>bold</strong> paragraph.</p>')"
Enter
Sleep 1.5s

Type "print(result.content)"
Enter
Sleep 2s

Type "exit()"
Enter
Sleep 1s
