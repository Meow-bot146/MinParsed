"""
MinCleaned - Intelligent HTML Content Extraction
MinParsed + Smart cleaning to extract only main content

Requires: minparsed.py (included in repo)

Removes:
- Navigation bars
- Footers
- Sidebars
- Boilerplate text
- Advertisements
- Social media widgets
"""

import re
from typing import List, Set, Tuple, Dict
from minparsed import MinParsed


class MinCleaned(MinParsed):
    """
    MinCleaned: Intelligent content extraction from HTML
    
    Extends MinParsed with smart algorithms to:
    - Detect and remove navigation
    - Filter out boilerplate
    - Extract main content only
    - Remove junk and ads
    """
    
    # Navigation indicators (class/id patterns)
    NAV_PATTERNS = [
        r'nav', r'menu', r'sidebar', r'header', r'footer',
        r'breadcrumb', r'widget', r'aside', r'banner',
        r'social', r'share', r'follow', r'subscribe',
        r'comment', r'discuss', r'related', r'recommend',
        r'advertisement', r'ad-', r'ads', r'promo',
        r'sponsored', r'partner', r'cookie', r'privacy',
    ]
    
    # Common boilerplate phrases
    BOILERPLATE_PHRASES = {
        'click here', 'read more', 'sign up', 'subscribe',
        'newsletter', 'follow us', 'share this', 'tweet',
        'facebook', 'twitter', 'instagram', 'linkedin',
        'copyright', 'all rights reserved', 'privacy policy',
        'terms of service', 'cookie policy', 'about us',
        'contact us', 'home', 'search', 'login', 'sign in',
    }
    
    # Content indicators
    CONTENT_TAGS = {
        'article', 'main', 'section', 'p', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'blockquote', 'pre', 'li'
    }
    
    def __init__(self):
        super().__init__()
        self.enable_cleaning = True
        
    def parse(self, html: str, clean: bool = True) -> str:
        """
        Parse HTML and extract clean content
        
        Args:
            html: Raw HTML string
            clean: Enable intelligent cleaning (default: True)
            
        Returns:
            Clean, readable main content
        """
        self.enable_cleaning = clean
        
        if not clean:
            # Just use MinParsed
            return super().parse(html)
        
        # Step 1: Pre-process - remove obvious junk
        html = self._remove_boilerplate_tags(html)
        
        # Step 2: Parse with MinParsed
        text = super().parse(html)
        
        # Step 3: Post-process - clean the text
        text = self._clean_boilerplate_text(text)
        text = self._filter_short_lines(text)
        text = self._remove_duplicate_lines(text)
        
        return text
    
    def _remove_boilerplate_tags(self, html: str) -> str:
        """Remove navigation, footer, sidebar tags based on attributes"""
        # Find and remove tags with nav-like class/id
        for pattern in self.NAV_PATTERNS:
            # Remove tags with matching class
            html = re.sub(
                rf'<(\w+)\s+[^>]*class=["\'][^"\']*\b{pattern}\b[^"\']*["\'][^>]*>.*?</\1>',
                '',
                html,
                flags=re.DOTALL | re.IGNORECASE
            )
            
            # Remove tags with matching id
            html = re.sub(
                rf'<(\w+)\s+[^>]*id=["\'][^"\']*\b{pattern}\b[^"\']*["\'][^>]*>.*?</\1>',
                '',
                html,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # Remove common boilerplate tags by name
        for tag in ['nav', 'aside', 'footer', 'header']:
            html = re.sub(
                rf'<{tag}\b[^>]*>.*?</{tag}>',
                '',
                html,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        return html
    
    def _clean_boilerplate_text(self, text: str) -> str:
        """Remove boilerplate phrases from text"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if line contains boilerplate
            is_boilerplate = False
            for phrase in self.BOILERPLATE_PHRASES:
                if phrase in line_lower:
                    # Only skip if the line is SHORT and mostly boilerplate
                    if len(line.split()) < 10:
                        is_boilerplate = True
                        break
            
            if not is_boilerplate:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _filter_short_lines(self, text: str, min_words: int = 3) -> str:
        """
        Remove very short lines (likely navigation/junk)
        
        Args:
            text: Input text
            min_words: Minimum words per line to keep
            
        Returns:
            Filtered text
        """
        lines = text.split('\n')
        filtered = []
        
        for line in lines:
            words = line.split()
            
            # Keep empty lines for paragraph separation
            if not line.strip():
                filtered.append(line)
                continue
            
            # Keep lines with enough words
            if len(words) >= min_words:
                filtered.append(line)
            # Also keep lines that look like headings (title case, <10 words)
            elif len(words) > 0 and len(words) < 10:
                # Check if it's title-like (starts with capital)
                if line[0].isupper() and not line.endswith('.'):
                    filtered.append(line)
        
        return '\n'.join(filtered)
    
    def _remove_duplicate_lines(self, text: str) -> str:
        """Remove duplicate consecutive lines"""
        lines = text.split('\n')
        cleaned = []
        prev_line = None
        
        for line in lines:
            if line != prev_line:
                cleaned.append(line)
            prev_line = line
        
        return '\n'.join(cleaned)
    
    def extract_main_content(self, html: str) -> str:
        """
        Extract main content with density-based algorithm
        
        This uses text density scoring to find the main content area
        
        Args:
            html: Raw HTML string
            
        Returns:
            Main content text
        """
        # Remove obvious junk first
        html = self._remove_boilerplate_tags(html)
        
        # Find content-rich sections
        sections = self._extract_content_sections(html)
        
        # Score sections by content density
        scored_sections = self._score_sections(sections)
        
        # Get top sections
        best_sections = sorted(scored_sections, key=lambda x: x[1], reverse=True)[:3]
        
        # Parse the best sections
        main_html = '\n'.join([s[0] for s in best_sections])
        
        # Parse with cleaning
        return self.parse(main_html, clean=True)
    
    def _extract_content_sections(self, html: str) -> List[str]:
        """Extract potential content sections from HTML"""
        sections = []
        
        # Look for article, main, section tags
        for tag in ['article', 'main', 'section', 'div']:
            pattern = rf'<{tag}\b[^>]*>(.*?)</{tag}>'
            matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
            sections.extend(matches)
        
        # Also get large paragraphs
        p_pattern = r'<p\b[^>]*>(.*?)</p>'
        paragraphs = re.findall(p_pattern, html, re.DOTALL | re.IGNORECASE)
        
        # Group consecutive paragraphs
        if paragraphs:
            sections.append(' '.join(paragraphs))
        
        return sections if sections else [html]
    
    def _score_sections(self, sections: List[str]) -> List[Tuple[str, float]]:
        """
        Score sections by content density
        
        Content density = (text length - link text length) / tag count
        
        Args:
            sections: List of HTML sections
            
        Returns:
            List of (section, score) tuples
        """
        scored = []
        
        for section in sections:
            # Calculate text length
            text = re.sub(r'<[^>]+>', '', section)
            text = text.strip()
            text_length = len(text)
            
            # Calculate link text length
            links = re.findall(r'<a\b[^>]*>(.*?)</a>', section, re.DOTALL | re.IGNORECASE)
            link_length = sum(len(link) for link in links)
            
            # Count tags
            tag_count = len(re.findall(r'<[^>]+>', section))
            
            # Calculate density score
            if tag_count > 0:
                # High text, low links, low tag density = good content
                content_text = text_length - link_length
                density = content_text / (tag_count + 1)
                
                # Bonus for paragraph tags
                p_count = len(re.findall(r'<p\b', section, re.IGNORECASE))
                density += p_count * 10
                
                # Penalty for nav indicators
                for pattern in self.NAV_PATTERNS:
                    if re.search(pattern, section, re.IGNORECASE):
                        density *= 0.5
                        break
                
                scored.append((section, density))
            else:
                scored.append((section, text_length))
        
        return scored


def clean_html(html: str) -> str:
    """
    Convenience function to extract clean content from HTML
    
    Args:
        html: Raw HTML string
        
    Returns:
        Clean main content text
    """
    cleaner = MinCleaned()
    return cleaner.parse(html, clean=True)


def extract_content(html: str) -> str:
    """
    Extract main content using density-based algorithm
    
    Args:
        html: Raw HTML string
        
    Returns:
        Main content text
    """
    cleaner = MinCleaned()
    return cleaner.extract_main_content(html)


# Benchmark comparison
def benchmark_mincleaned():
    """Benchmark MinCleaned"""
    import time
    
    # Realistic webpage with navigation, footer, ads
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Article Title</title>
    </head>
    <body>
        <nav class="navbar">
            <a href="/">Home</a>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </nav>
        
        <div class="sidebar">
            <h3>Popular Posts</h3>
            <ul>
                <li><a href="#">Post 1</a></li>
                <li><a href="#">Post 2</a></li>
            </ul>
            <div class="advertisement">
                <p>Buy now! Click here!</p>
            </div>
        </div>
        
        <main>
            <article>
                <h1>Main Article Title</h1>
                <p>This is the actual content that we want to extract.</p>
                <p>It contains multiple paragraphs of meaningful text.</p>
                <p>This is important information that the user came for.</p>
                <blockquote>An important quote from an expert.</blockquote>
                <p>More valuable content continues here.</p>
            </article>
        </main>
        
        <aside class="related">
            <h3>Related Articles</h3>
            <ul>
                <li><a href="#">Related 1</a></li>
                <li><a href="#">Related 2</a></li>
            </ul>
        </aside>
        
        <footer>
            <p>Copyright 2026. All rights reserved.</p>
            <p>Privacy Policy | Terms of Service</p>
            <div class="social">
                <a href="#">Facebook</a>
                <a href="#">Twitter</a>
            </div>
        </footer>
    </body>
    </html>
    """ * 50  # Repeat for benchmark
    
    # Benchmark MinCleaned
    start = time.time()
    result = clean_html(html)
    end = time.time()
    
    print(f"MinCleaned processed {len(html):,} bytes in {(end-start)*1000:.2f}ms")
    print(f"Speed: {len(html)/(end-start)/1024/1024:.2f} MB/s")
    print()
    print("Cleaned output:")
    print(result)


if __name__ == "__main__":
    # Example usage
    html = """
    <html>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/about">About</a>
        </nav>
        
        <article>
            <h1>Article Title</h1>
            <p>This is the main content.</p>
            <p>It has multiple paragraphs.</p>
        </article>
        
        <footer>
            <p>Copyright 2026</p>
        </footer>
    </body>
    </html>
    """
    
    print("=" * 60)
    print("MinCleaned Example")
    print("=" * 60)
    print()
    
    cleaner = MinCleaned()
    text = cleaner.parse(html, clean=True)
    print(text)
    
    print()
    print("=" * 60)
    print("Running benchmark...")
    print("=" * 60)
    benchmark_mincleaned()
