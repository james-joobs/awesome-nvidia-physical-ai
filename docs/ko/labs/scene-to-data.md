# CAD 작업대에서 센서 데이터까지

## 동작 원리

CadQuery로 작업대 STEP을 저장한 뒤 다시 읽습니다. 읽어 온 솔리드를 미터 단위 삼각형 메시로 만들어 OpenUSD에 배치합니다. PhysX로 상판 위에 큐브를 떨어뜨리고, Replicator로 검사 카메라의 RGB·깊이·의미 분할을 저장합니다. 큐브 마스크 안의 깊이값을 카메라 좌표에서 월드 좌표로 옮기면 화면과 같은 점군이 나옵니다. [작업대 USD](../../../labs/scene-to-data/workbench_scene.usda) · [점군 재생 씬](../../../labs/scene-to-data/rgbd-surface.usda)

## 따라 하기

Python, NumPy, `usd-core`만으로 저장된 카메라 데이터에서 점군과 이동량을 다시 계산할 수 있습니다. [카메라 데이터 네 세트](../../../labs/scene-to-data/replicator-data.zip)를 작업대 USD 옆에 풉니다.

```sh
mkdir -p ./runs/cad
cp labs/scene-to-data/workbench_scene.usda ./runs/cad/
unzip labs/scene-to-data/replicator-data.zip -d ./runs/cad
python labs/scene-to-data/backproject.py ./runs/cad ./runs/point-cloud
```

데이터를 새로 만들려면 첫 줄은 CadQuery 환경에서, 둘째 줄은 RTX GPU와 화면이 연결된 Isaac Sim 6.2 환경에서 실행합니다.

```sh
python labs/scene-to-data/make_step.py ./runs/cad-new
python labs/scene-to-data/workbench_final_take.py ./runs/cad-new/cad_meshes.json ./runs/cad-new
python labs/scene-to-data/backproject.py ./runs/cad-new ./runs/point-cloud-new
```

4×4 영상에 나온 장면 무작위화와 12프레임 생성은 [Replicator 실습](replicator-outputs.md)에서 따라 할 수 있습니다.

## 테스트 결과

STEP을 다시 읽어 상판의 가로·세로·두께가 1,200 × 600 × 40mm인지 검사했습니다. 큐브 중심은 0.8615m에서 멈췄습니다. 네 장의 점군에서 계산한 X축 이동량의 최대 오차는 약 5.3mm였습니다. 첫 프레임에서 보이는 표면을 기준으로 이동량을 비교한 값입니다. [촬영 당시 측정값](../../../labs/scene-to-data/recorded.json)
