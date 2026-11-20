# Security and publication checks

Please report a suspected exposed credential privately through GitHub's security reporting feature if available. Do not copy a credential or private machine information into a public issue.

Before publishing lab artifacts:

- Keep private hostnames, home directories, device UUIDs, credentials and original operational logs out of the repository and media.
- Publish the measurements, software versions, public source revisions and hardware requirements needed to reproduce a lab. Use repository-relative paths or clearly documented placeholders in receipts.
- Inspect image metadata, model debug information, USD layers and archive contents as well as visible text. Check recordings for terminal prompts, addresses and private files before encoding them.
- When metadata changes, verify pixels, model outputs and lab results as appropriate, then update the publication hashes. A random-input model check verifies an interface, not task performance.

GitHub Secret Scanning and Push Protection complement the repository checks. The `Check publication privacy` workflow runs on pull requests and main pushes. Pages runs the same checks **before uploading** its site artifact.

For local inspection, install `scripts/requirements-publication.txt` in a separate Python environment, then run:

```sh
python scripts/check-public-artifacts.py
python -m unittest discover -s scripts -p test_public_artifacts.py
```

A trusted maintainer configures the `PUBLICATION_PRIVATE_NAMES` repository Actions secret as a comma- or newline-separated list of private machine names. The checker reads that environment variable locally too. It reports file names and rule categories, never matching private values. Fork pull requests do not receive repository secrets; generic checks still run, and trusted Pages publication requires the denylist to be configured.

`scripts/ci-publication-checks.sh` also runs pinned, checksum-verified Gitleaks on the tracked publication files. On non-Linux systems, set `GITLEAKS_BIN` to an installed Gitleaks 8.30.1 executable. The artifact checker decodes image metadata and USD layers inside archives; recording pixels still require a separate visual/OCR review.

Changing current files does not remove old commits, tags, clones or caches. Credential exposure requires revocation or rotation. Coordinate any published-history rewrite with maintainers and users of existing clones. [GitHub's removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## 한국어

인증정보나 개인 장비 정보가 노출된 것 같다면 공개 이슈에 값을 복사하지 말고, 제공되는 경우 GitHub의 비공개 보안 신고 기능을 이용해 주세요.

실습의 입력·출력·수치 결과와 필요한 버전 정보는 유지하되, 개인 서버 이름·홈 디렉터리·장비 식별자·인증정보·원본 운영 로그는 공개 자료에서 제외합니다. 이미지 메타데이터, 모델 디버그 정보, USD·압축 파일 내부와 녹화 화면도 확인해야 합니다.

메타데이터를 정리한 경우 이미지 픽셀·모델 출력·실습 결과가 유지되는지 확인하고 파일 해시를 갱신합니다. 위 명령으로 로컬 검사와 회귀 테스트를 실행할 수 있습니다. 검사 결과에는 비공개 값을 출력하지 않습니다. 비공개 머신 이름 목록은 관리자만 Actions secret으로 설정하며, 외부 포크의 PR에는 전달되지 않습니다.

자동 검사는 이미지 메타데이터·압축 파일·USD 레이어 등을 확인합니다. 영상의 실제 픽셀은 별도 육안·OCR 검토가 필요합니다. Pages 배포는 공개 전 검사를 통과한 뒤 진행합니다. 현재 파일을 수정해도 과거 커밋과 복사본은 남으므로, 이력 재작성과 인증정보 폐기·교체는 별도 절차로 처리합니다.
