# -*- coding: utf-8 -*-
from app import create_app
import config
app = create_app(config=config.Config)

if __name__ == '__main__':
    # 程序入口
    app.run(debug=True)