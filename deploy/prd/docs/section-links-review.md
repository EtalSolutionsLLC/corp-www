# External section links and viewport alignment

## Confirmed failure

Live-site Chromium checks reproduced a fresh `/#lab` landing at Home (scroll position 0). Other hash landings and a clicked lab link retained an extra header-height gap: section top 168px with header bottom 84px. The viewport alignment script was deferred after external footer resources, so those resources could hold up the corrective navigation. Native anchor navigation applies both the page scroll padding and target scroll margin while the script is waiting.

## Changed files and sections

- `www/assets/js/viewport-targets.js`, `alignCurrentHashTarget`: corrective scrolling explicitly uses instant behavior, independent of the document's smooth-scroll style.
- `www/partials/footer.html`, before external policy resources: run the independent viewport script after section/header/footer markup and before external footer stylesheet/script loading can block it. Cache version increased to 124.
- `www/index.html`, footer/script placement: applies the canonical footer ordering and removes the old deferred duplicate near the collection scripts.
- `www/trust/index.html`, footer/script placement: same shared footer ordering and duplicate removal.
- `docs/section-links-review.md`: this review and verification record.

## Verification

23 existing viewport tests passed. JavaScript syntax and focused diff formatting passed. Chromium exercised fresh `#lab`, `#lab-proof`, `#services` landings and clicking the Home lab link, with normal resources and with external resources intentionally left pending. Desktop section tops matched the measured 84px header bottom (the nested lab heading was within half a pixel). Mobile checks use the same live header measurement. No new repository tests were added.

Changes are in the local `/home/davidomer/code/corp-www` source. Production has not been redeployed by Codex. Rebuild/deploy this site through its normal flow before checking the live URLs. No deployment files were inspected or edited; no ReviewNudge source was changed for this fix.

Mobile results: the measured header bottom was 112px; all four exercised section landings aligned within 0.36px of it. An additional header test group passed three checks and failed one existing desktop navigation-spacing assertion (expected `clamp(16px, 1.6vw, 28px)`, current CSS uses `clamp(14px, 1.3vw, 22px)`). Repeating the test against the committed HEAD stylesheet reproduced the same failure; that stylesheet is unchanged by this fix.

## Fast visible scrolling follow-up

At David’s request, `www/assets/js/viewport-targets.js` now animates section alignment over 240ms with an ease-out curve. Corrective passes update the destination without restarting the animation, so the section still finishes below the measured header. Reduced-motion preferences retain immediate alignment. Individual animation frames use instant positioning to prevent the browser's separate smooth-scroll behavior from competing with the timed animation. This supersedes the earlier immediate-navigation behavior.

The 23 existing viewport checks, syntax and focused formatting checks passed. Chromium checks with external resources pending verify direct hash landing and clicked navigation still finish at the measured header edge; an intermediate sample verifies visible movement before the final position. No new repository tests added.

## Slower animation trial

- `www/assets/js/viewport-targets.js`, timed alignment animation: increased duration from 240ms to 550ms at David’s request. Ease-out, destination correction, and reduced-motion handling remain unchanged. This supersedes the 240ms duration above.
- Chromium confirmed visible intermediate movement and final header alignment with external resources pending. All 23 existing viewport checks, syntax and focused formatting checks passed.
- David will review the feel after rebuilding; return to native smooth scrolling if requested. Not deployed by Codex.

## Restore native smooth scrolling

- `www/assets/js/viewport-targets.js`, `alignCurrentHashTarget`: removed the custom animation and its state. Section navigation now explicitly uses the browser’s native smooth scrolling, with immediate alignment only for reduced-motion preferences. This supersedes both fixed-duration experiments.
- The earlier script placement fix remains, so external footer resources do not delay initial section navigation.
- Chromium confirmed intermediate movement and final header alignment for direct hash links and clicked navigation with external resources pending. All 23 existing viewport checks, syntax and focused formatting checks passed. Changes remain local pending rebuild/deploy.
