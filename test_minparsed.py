"""
MinParsed Test Suite
Comprehensive tests for HTML parsing
"""

from minparsed import MinParsed, parse_html

def test_basic_text():
    """Test basic text extraction"""
    html = "<p>Hello, World!</p>"
    result = parse_html(html)
    assert result == "Hello, World!", f"Expected 'Hello, World!', got '{result}'"
    print("✓ Basic text extraction")

def test_nested_tags():
    """Test nested tags"""
    html = "<div><p>Outer <span>inner</span> text</p></div>"
    result = parse_html(html)
    assert "Outer inner text" in result
    print("✓ Nested tags")

def test_block_elements():
    """Test block elements create line breaks"""
    html = "<p>Para 1</p><p>Para 2</p><p>Para 3</p>"
    result = parse_html(html)
    lines = result.split('\n')
    assert len(lines) == 3
    assert lines[0] == "Para 1"
    assert lines[1] == "Para 2"
    assert lines[2] == "Para 3"
    print("✓ Block elements")

def test_skip_script():
    """Test script tags are skipped"""
    html = "<p>Before</p><script>alert('bad');</script><p>After</p>"
    result = parse_html(html)
    assert "alert" not in result
    assert "Before" in result
    assert "After" in result
    print("✓ Script tag skipping")

def test_skip_style():
    """Test style tags are skipped"""
    html = "<p>Text</p><style>.test { color: red; }</style><p>More</p>"
    result = parse_html(html)
    assert "color" not in result
    assert "Text" in result
    assert "More" in result
    print("✓ Style tag skipping")

def test_html_entities():
    """Test HTML entity decoding"""
    html = "<p>&amp; &lt; &gt; &quot; &nbsp;</p>"
    result = parse_html(html)
    assert "&" in result
    assert "<" in result
    assert ">" in result
    assert '"' in result
    print("✓ HTML entities")

def test_numeric_entities():
    """Test numeric HTML entities"""
    html = "<p>&#65; &#x42; &#169;</p>"
    result = parse_html(html)
    assert "A" in result  # &#65;
    assert "B" in result  # &#x42;
    assert "©" in result  # &#169;
    print("✓ Numeric entities")

def test_comments():
    """Test HTML comments are removed"""
    html = "<p>Text</p><!-- Comment --><p>More</p>"
    result = parse_html(html)
    assert "Comment" not in result
    assert "Text" in result
    assert "More" in result
    print("✓ Comment removal")

def test_whitespace_normalization():
    """Test whitespace is normalized"""
    html = "<p>Multiple     spaces    here</p>"
    result = parse_html(html)
    assert "Multiple spaces here" in result
    print("✓ Whitespace normalization")

def test_br_tags():
    """Test <br> tags create line breaks"""
    html = "<p>Line 1<br>Line 2<br>Line 3</p>"
    result = parse_html(html)
    lines = result.split('\n')
    assert len(lines) >= 3
    print("✓ BR tags")

def test_lists():
    """Test list extraction"""
    html = """
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    """
    result = parse_html(html)
    assert "Item 1" in result
    assert "Item 2" in result
    assert "Item 3" in result
    print("✓ Lists")

def test_tables():
    """Test table extraction"""
    html = """
    <table>
        <tr><td>Cell 1</td><td>Cell 2</td></tr>
        <tr><td>Cell 3</td><td>Cell 4</td></tr>
    </table>
    """
    result = parse_html(html)
    assert "Cell 1" in result
    assert "Cell 2" in result
    assert "Cell 3" in result
    assert "Cell 4" in result
    print("✓ Tables")

def test_headings():
    """Test headings extraction"""
    html = """
    <h1>Title</h1>
    <h2>Subtitle</h2>
    <p>Content</p>
    """
    result = parse_html(html)
    lines = result.split('\n')
    assert "Title" in lines
    assert "Subtitle" in lines
    assert "Content" in lines
    print("✓ Headings")

def test_messy_html():
    """Test handling of messy HTML"""
    html = """
    <div class="test" id="main" style="color:red">
        <p>Text with <strong>bold</strong> and <em>italic</em></p>
        <div><span>Nested <a href="#">link</a> text</span></div>
    </div>
    """
    result = parse_html(html)
    assert "Text with bold and italic" in result
    assert "Nested link text" in result
    print("✓ Messy HTML")

def test_empty_tags():
    """Test empty tags don't add extra whitespace"""
    html = "<p></p><div></div><p>Text</p><span></span>"
    result = parse_html(html)
    assert result.strip() == "Text"
    print("✓ Empty tags")

def test_malformed_html():
    """Test handling of malformed HTML"""
    html = "<p>Unclosed paragraph<div>Another <b>tag"
    result = parse_html(html)
    assert "Unclosed paragraph" in result
    assert "Another" in result
    assert "tag" in result
    print("✓ Malformed HTML")

def test_unicode():
    """Test Unicode text handling"""
    html = "<p>Hello 世界 🌍</p>"
    result = parse_html(html)
    assert "Hello 世界 🌍" in result
    print("✓ Unicode")

def test_long_text():
    """Test handling of long text"""
    html = "<p>" + ("word " * 1000) + "</p>"
    result = parse_html(html)
    assert "word" in result
    assert len(result) > 1000
    print("✓ Long text")

def test_special_entities():
    """Test special HTML entities"""
    html = "<p>&copy; &reg; &trade; &mdash; &ndash;</p>"
    result = parse_html(html)
    assert "©" in result
    assert "®" in result
    assert "™" in result
    print("✓ Special entities")

def test_cdata():
    """Test CDATA sections are removed"""
    html = "<p>Before</p><![CDATA[skip this]]><p>After</p>"
    result = parse_html(html)
    assert "skip this" not in result
    assert "Before" in result
    assert "After" in result
    print("✓ CDATA removal")

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("MinParsed Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        test_basic_text,
        test_nested_tags,
        test_block_elements,
        test_skip_script,
        test_skip_style,
        test_html_entities,
        test_numeric_entities,
        test_comments,
        test_whitespace_normalization,
        test_br_tags,
        test_lists,
        test_tables,
        test_headings,
        test_messy_html,
        test_empty_tags,
        test_malformed_html,
        test_unicode,
        test_long_text,
        test_special_entities,
        test_cdata,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__}: ERROR - {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Tests Passed: {passed}/{len(tests)}")
    print(f"Tests Failed: {failed}/{len(tests)}")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
