## Consumers outside the diff

| consumer | what the change does to it | proved? |
|---|---|---|
| `src/main/java/lib/member/MemberLookupService.java:57` | Looks up `+4930…` now. The 40,000 stored rows were written by the old `MemberImport` as `004930…`, and `findByPhone` is `where phone = :phone`, so no existing member is found by phone. | Breaks. Prove with the test below. |
| `src/main/java/lib/member/MemberImport.java:28` | Writes `+…` from now on, so `members.phone` holds two formats. | Breaks consistency. |
| `src/main/java/lib/sms/SmsSender.java:41` | Sends `+…` to the gateway instead of `00…`. Whether the gateway accepts `+` is not shown. | Unproved. Needs a gateway contract test. |

"Nothing else changes" does not hold.

## The run that proves it

```java
@DataJpaTest
class PhoneLookupAfterFormatChangeTest {
    @Autowired MemberRepository members;

    @Test
    void finds_a_member_stored_in_the_old_format() {
        members.save(memberWithPhone("004930123456"));
        final var lookup = new MemberLookupService(members);
        assertThat(lookup.byPhone("+49 30 123456")).isPresent();
    }
}
```

This test fails on the diff. Also run `select count(*) from members where phone like '00%'` on a replica to size the break.

## Ask

1. Add a migration that rewrites `members.phone` from `00…` to `+…` in the same change.
2. Add the test above and a contract test for the SMS gateway with a `+` number.
3. Split the cleanup from the format change if the migration is large.

Verdict: request changes.
