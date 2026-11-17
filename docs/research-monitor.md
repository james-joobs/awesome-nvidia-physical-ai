# 피지컬 AI 연구 수집 운영

[GitHub Actions 실행 기록](https://github.com/james-joobs/awesome-nvidia-physical-ai/actions/workflows/collect-research.yml) · [최신 수집 보고서](https://github.com/james-joobs/awesome-nvidia-physical-ai/blob/research-reports/latest.md)

GitHub Actions는 매일 09:17 KST에 공식 출처에서 변경 후보를 수집합니다. Actions에서 **Run workflow**를 선택해 수동으로 실행할 수도 있습니다. 보고서는 `research-reports` 브랜치에 저장됩니다.

- `latest.md`에는 최근 7일간의 후보, 출처별 마지막 성공 시각과 확인 오류가 나옵니다. 금요일 스냅샷은 `weekly.md`에 저장됩니다.
- 지정된 GitHub 저장소의 릴리스와 루트 라이선스, NVIDIA 관련 조직의 새 공개 저장소, 선정한 Hugging Face 모델·데이터셋, NVIDIA Robotics 기술 블로그, NVIDIA Research 사이트맵, 관련 arXiv 논문을 확인합니다.
- GitHub 릴리스·Hub 목록과 피드는 최신 결과 범위에서 확인합니다. 출처가 일시적으로 실패하면 최근 확인 결과를 보존하고, 다음에 마지막 성공 시점까지 조회 기간을 넓힙니다. 긴 공백이나 피드에서 빠진 발표는 공식 페이지에서 추가 확인합니다.
- 검토할 후보는 양 언어 카탈로그나 연구 가이드의 PR로 반영합니다. 코드·가중치·데이터 이용 조건은 각각 원문을 확인합니다. PR이 `main`에 병합되면 기존 Pages 배포가 이어집니다.

## Mac에서 자동으로 받기

첫 보고서가 올라간 후 이 레포에서 아래 명령을 실행합니다.

```sh
./scripts/install-macos-research-sync.sh
```

기본 보관 위치는 `~/work/awesome-nvidia-physical-ai-reports/`입니다. 다른 위치는 절대 경로를 첫 인수로 전달합니다. 로그인할 때와 매시 07분·37분에 전용 체크아웃을 업데이트합니다. Mac이 꺼져 있는 동안에는 GitHub가 수집을 이어가고, 다음 로그인에서 보고서 브랜치의 최신 커밋을 받습니다.

보고서 체크아웃에서 읽거나 복사할 수 있습니다. 파일을 편집하면 안전한 빠른 감기 업데이트가 실패할 수 있습니다. 오류 기록은 `~/Library/Logs/physical-ai-research-sync.log`에 남습니다.
