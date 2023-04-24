数码相机 接口的环境部署
==================

准备工作
-------

    数码相机服务，需求：ubuntu系统，数码相机与usb接口

构建
----

    # docker build -f ./Dockerfile capture-image:dc bash

运行
----

    # docker run -t -i --device=/dev/bus/usb -p 9210:8099  capture-image:dc bash
