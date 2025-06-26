use esp32_hid_rs::layout::char_to_hid;

#[test]
fn test_ascii_letters() {
    // a-z
    for (i, c) in ('a'..='z').enumerate() {
        let (modif, code) = char_to_hid(c).unwrap();
        assert_eq!(modif, 0);
        assert_eq!(code, 0x04 + i as u8);
    }
    // A-Z
    for (i, c) in ('A'..='Z').enumerate() {
        let (modif, code) = char_to_hid(c).unwrap();
        assert_eq!(modif, 0x02);
        assert_eq!(code, 0x04 + i as u8);
    }
}

#[test]
fn test_ascii_digits_and_symbols() {
    assert_eq!(char_to_hid('1'), Some((0, 0x1E)));
    assert_eq!(char_to_hid('!'), Some((0x02, 0x1E)));
    assert_eq!(char_to_hid('0'), Some((0, 0x27)));
    assert_eq!(char_to_hid(')'), Some((0x02, 0x27)));
    assert_eq!(char_to_hid(' '), Some((0, 0x2C)));
    assert_eq!(char_to_hid('\n'), Some((0, 0x28)));
    assert_eq!(char_to_hid('\t'), Some((0, 0x2B)));
    assert_eq!(char_to_hid('-'), Some((0, 0x2D)));
    assert_eq!(char_to_hid('_'), Some((0x02, 0x2D)));
    assert_eq!(char_to_hid('='), Some((0, 0x2E)));
    assert_eq!(char_to_hid('+'), Some((0x02, 0x2E)));
}

#[test]
fn test_unknown_char() {
    assert_eq!(char_to_hid('€'), None);
    assert_eq!(char_to_hid('ě'), None); // zatím není implementováno
} 