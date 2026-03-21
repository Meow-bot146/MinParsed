"""
MinParsed - Minimal HTML-to-Text Parser
Ultra-fast, lightweight HTML text extraction with smart reconstruction
"""

import re
from typing import List, Set

class MinParsed:
    """
    MinParsed: High-speed HTML-to-text parser
    
    Features:
    - No dependencies (pure Python)
    - Blazing fast (regex-based)
    - Smart text reconstruction
    - Handles messy HTML
    - Preserves semantic structure
    """
    
    # Block-level tags that should add line breaks
    BLOCK_TAGS = {
        'p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'li', 'tr', 'br', 'hr', 'blockquote', 'pre',
        'article', 'section', 'header', 'footer', 'main',
        'aside', 'nav', 'table', 'thead', 'tbody', 'tfoot',
        'dd', 'dt', 'fieldset', 'figcaption', 'figure',
        'address', 'details', 'summary'
    }
    
    # Tags to completely skip (including content)
    SKIP_TAGS = {
        'script', 'style', 'noscript', 'svg', 'math',
        'iframe', 'object', 'embed', 'applet'
    }
    
    # Inline tags that might need space
    INLINE_TAGS = {
        'a', 'span', 'strong', 'b', 'em', 'i', 'u',
        'small', 'mark', 'del', 'ins', 'sub', 'sup',
        'code', 'kbd', 'samp', 'var', 'abbr', 'cite',
        'q', 'dfn', 'time', 'data'
    }
    
    def __init__(self):
        self.text_parts: List[str] = []
        
    def parse(self, html: str) -> str:
        """
        Parse HTML and extract clean text
        
        Args:
            html: Raw HTML string
            
        Returns:
            Clean, readable text
        """
        # Reset state
        self.text_parts = []
        
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        # Remove CDATA sections
        html = re.sub(r'<!\[CDATA\[.*?\]\]>', '', html, flags=re.DOTALL)
        
        # Remove skip tags and their content
        for tag in self.SKIP_TAGS:
            html = re.sub(
                rf'<{tag}\b[^>]*>.*?</{tag}>',
                '',
                html,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # Process the HTML
        self._process_html(html)
        
        # Join and clean
        text = '\n'.join(self.text_parts)
        text = self._clean_text(text)
        
        return text
    
    def _process_html(self, html: str):
        """Process HTML and extract text with structure"""
        pos = 0
        current_text = []
        
        while pos < len(html):
            # Find next tag
            tag_start = html.find('<', pos)
            
            if tag_start == -1:
                # No more tags, get remaining text
                text = html[pos:]
                if text.strip():
                    current_text.append(text)
                break
            
            # Get text before tag
            if tag_start > pos:
                text = html[pos:tag_start]
                if text.strip():
                    current_text.append(text)
            
            # Find tag end
            tag_end = html.find('>', tag_start)
            if tag_end == -1:
                # Malformed HTML, skip rest
                break
            
            # Extract tag
            tag = html[tag_start:tag_end + 1]
            
            # Check if it's a block tag
            tag_name = self._get_tag_name(tag)
            
            if tag_name in self.BLOCK_TAGS:
                # Flush current text and add line break
                if current_text:
                    self.text_parts.append(' '.join(current_text))
                    current_text = []
                
                # Special handling for <br>
                if tag_name == 'br':
                    self.text_parts.append('')
            
            # Move past this tag
            pos = tag_end + 1
        
        # Flush any remaining text
        if current_text:
            self.text_parts.append(' '.join(current_text))
    
    def _get_tag_name(self, tag: str) -> str:
        """Extract tag name from tag string"""
        # Remove < and >
        tag = tag.strip('<>')
        
        # Handle closing tags
        if tag.startswith('/'):
            tag = tag[1:]
        
        # Get just the tag name (before space or /)
        match = re.match(r'([a-zA-Z0-9]+)', tag)
        if match:
            return match.group(1).lower()
        return ''
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Decode HTML entities
        text = self._decode_entities(text)
        
        # Normalize whitespace within lines
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Replace multiple spaces with single space
            line = re.sub(r'[ \t]+', ' ', line)
            # Strip leading/trailing whitespace
            line = line.strip()
            # Only keep non-empty lines
            if line:
                cleaned_lines.append(line)
        
        # Remove excessive blank lines (max 1 blank line between paragraphs)
        result = []
        prev_empty = False
        
        for line in cleaned_lines:
            if not line:
                if not prev_empty:
                    result.append(line)
                prev_empty = True
            else:
                result.append(line)
                prev_empty = False
        
        return '\n'.join(result)
    
    def _decode_entities(self, text: str) -> str:
        """Decode common HTML entities"""
        entities = {
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&apos;': "'",
            '&nbsp;': ' ',
            '&ndash;': '–',
            '&mdash;': '—',
            '&lsquo;': ''',
            '&rsquo;': ''',
            '&ldquo;': '"',
            '&rdquo;': '"',
            '&hellip;': '…',
            '&copy;': '©',
            '&reg;': '®',
            '&trade;': '™',
        }
        
        for entity, char in entities.items():
            text = text.replace(entity, char)
        
        # Handle numeric entities (&#123; or &#xAB;)
        text = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), text)
        text = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), text)
        
        return text


def parse_html(html: str) -> str:
    """
    Convenience function to parse HTML to text
    
    Args:
        html: Raw HTML string
        
    Returns:
        Clean text
    """
    parser = MinParsed()
    return parser.parse(html)


# Quick benchmark comparison
def benchmark_minparsed():
    """Simple benchmark test"""
    import time
    
    # Test HTML
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <script>alert('skip me');</script>
        <style>.test { color: red; }</style>
    </head>
    <body>
        <h1>Welcome to MinParsed</h1>
        <p>This is a <strong>fast</strong> and <em>minimal</em> HTML parser.</p>
        
        <div class="content">
            <p>It handles:</p>
            <ul>
                <li>Block elements</li>
                <li>Inline elements</li>
                <li>HTML entities like &amp; and &nbsp;</li>
                <li>Messy &lt;html&gt; with lots of tags</li>
            </ul>
        </div>
        
        <footer>
            <p>&copy; 2026 MinParsed</p>
        </footer>
        
        <script>console.log('more to skip');</script>
    </body>
    </html>
    """ * 100  # Repeat 100 times for benchmark
    
    # Benchmark MinParsed
    start = time.time()
    result = parse_html(html)
    end = time.time()
    
    print(f"MinParsed processed {len(html):,} bytes in {(end-start)*1000:.2f}ms")
    print(f"Speed: {len(html)/(end-start)/1024/1024:.2f} MB/s")
    print()
    print("Sample output (first 500 chars):")
    print(result[:500])


if __name__ == "__main__":
    # Example usage
    html = """
    <html>
    <head><title>Example</title></head>
    <body>
        <h1>Hello, World!</h1>
        <p>This is a <strong>test</strong> of MinParsed.</p>
        <p>It extracts clean text from messy HTML.</p>
        <script>alert('This will be skipped');</script>
        <div>
            <p>Handles &amp; entities &nbsp; too!</p>
        </div>
    </body>
    </html>
    """
    
    parser = MinParsed()
    text = parser.parse(html)
    print(text)
    print()
    print("=" * 60)
    print("Running benchmark...")
    print("=" * 60)
    benchmark_minparsed()
