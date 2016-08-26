# peach-web

## 設定ファイルについて

設定ファイルは以下の優先順位で読み込まれます。

- 共通の設定 `peach-web/config/default.py`
- 環境変数 `PROFILE` を指定しなかった場合 `peach-web/config/config.py`
- 環境変数 `PROFILE` を指定した場合 `peach-web/config/{PROFILE}`

## 単体で動かす方法

- 依存しているモジュールをインストール
```
pyvenv venv
source venv/bin/activate
pip install -r requirements.txt
pip install git+https://github.com/recochoku-sys/peach-swagger-client.git
```

- 起動
```
export PROFILE=demo.py
python manage.py runserver --port 5000
```

## Jenkinsの設定

```
# テストしない間は不要
#
# rm -rf venv/
# virtualenv-3.4 venv
# source venv/bin/activate
# pip install -r requirements.txt
# pip install -e ../peach-swagger-client/
#
# nosetests tests/
#

cd /var/lib/jenkins/workspace/
docker build -t web -f peach-web/Dockerfile .

aws ecr get-login --region us-east-1 | /bin/bash
docker tag web:latest 684460453570.dkr.ecr.us-east-1.amazonaws.com/peach-web:latest
docker push 684460453570.dkr.ecr.us-east-1.amazonaws.com/peach-web:latest
docker rmi 684460453570.dkr.ecr.us-east-1.amazonaws.com/peach-web:latest
docker rmi web:latest
docker logout https://684460453570.dkr.ecr.us-east-1.amazonaws.com
```

## CDNに配置

```
cd web/static/cdn
aws s3 cp --recursive ./ s3://peach-resource-dev/common/
```
