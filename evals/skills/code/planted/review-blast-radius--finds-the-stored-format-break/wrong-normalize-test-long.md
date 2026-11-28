## Review

The change flips the prefix rule. A unit test pins it:

```java
@ParameterizedTest
@CsvSource({"0049 30 123456, +4930123456", "+49 30 123456, +4930123456", "030 123456, 030123456"})
void normalizes_to_e164(final String raw, final String expected) {
    assertThat(PhoneNumbers.normalize(raw)).isEqualTo(expected);
}
```

| consumer | effect |
|---|---|
| `SmsSender.java:41` | gets E.164 |
| `MemberLookupService.java:57` | gets E.164 |
| `MemberImport.java:28` | gets E.164 |

With the test in place, the callers are fine. Approve after the test is added.
