# 피지컬 AI 연구 수집 운영

[GitHub Actions 실행 기록](https://github.com/james-joobs/awesome-nvidia-physical-ai/actions/workflows/collect-research.yml) · [최신 수집 보고서](https://github.com/james-joobs/awesome-nvidia-physical-ai/blob/research-reports/latest.md)

GitHub Actions는 매일 09:17 KST에 공식 출처에서 변경 후보를 수집합니다. Actions에서 **Run workflow**를 선택해 수동으로 실행할 수도 있습니다. 보고서는 `research-reports` 브랜치에 저장됩니다.

- `latest.md`에는 최근 7일간의 후보, 출처별 마지막 성공 시각과 확인 오류가 나옵니다. 금요일 스냅샷은 `weekly.md`에 저장됩니다.
- 지정된 GitHub 저장소의 릴리스와 루트 라이선스, NVIDIA 관련 조직의 새 공개 저장소, 선정한 Hugging Face 모델·데이터셋, NVIDIA Robotics 기술 블로그, NVIDIA Research 사이트맵, 관련 arXiv 논문을 확인합니다.
- GitHub 릴리스·Hub 목록과 피드는 최신 결과 범위에서 확인합니다. 출처가 일시적으로 실패하면 최근 확인 결과를 보존하고, 다음에 마지막 성공 시점까지 조회 기간을 넓힙니다. 긴 공백이나 피드에서 빠진 발표는 공식 페이지에서 추가 확인합니다.
- 금요일에는 수집 작업 뒤에 최근 후보를 다시 확인합니다. 이미 문서에 반영됐거나 열려 있는 자동 검토 PR에 포함된 출처는 건너뜁니다. 릴리스는 버전별로 확인합니다.
- 공식 저장소·릴리스, 모델·데이터 카드 및 연구 원문에서 확인한 공개 범위와 이용 조건을 같은 출처를 사용한 영문·한국어 초안에 기입합니다. 확인할 수 없는 연구 코드·가중치는 미확인으로 표시합니다. 카탈로그에 자동으로 추가하는 코드·가중치·데이터는 라이선스 근거를 확인한 항목입니다.
- 사이트 빌드·검색 테스트·실습 검증을 통과하면 `automation/research-YYYY-MM-DD` 브랜치로 주간 초안 PR을 엽니다. 새로 반영할 내용이 있을 때 PR이 생성됩니다. 운영자가 검토 후 `main`에 병합하면 Pages에 배포됩니다.
- Actions에서 **Run workflow**의 **review_preview**를 선택하면 수집, 초안 작성, 검증을 실행합니다. 변경분은 실행 상세의 **weekly-research-review** 아티팩트에서 볼 수 있습니다.

## Mac에서 자동으로 받기

첫 보고서가 올라간 후 이 레포에서 아래 명령을 실행합니다.

```sh
./scripts/install-macos-research-sync.sh
```

기본 보관 위치는 `~/work/awesome-nvidia-physical-ai-reports/`입니다. 다른 위치는 절대 경로를 첫 인수로 전달합니다. 로그인할 때와 매시 07분·37분에 전용 체크아웃을 업데이트합니다. Mac이 꺼져 있는 동안에는 GitHub가 수집을 이어가고, 다음 로그인에서 보고서 브랜치의 최신 커밋을 받습니다.

보고서 체크아웃에서 읽거나 복사할 수 있습니다. 파일을 편집하면 안전한 빠른 감기 업데이트가 실패할 수 있습니다. 오류 기록은 `~/Library/Logs/physical-ai-research-sync.log`에 남습니다.
