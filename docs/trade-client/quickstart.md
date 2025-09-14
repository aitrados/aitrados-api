---
weight: 100
date: "2023-05-03T22:37:22+01:00"
draft: false
author: "VON"
title: "Quickstart"
icon: "rocket_launch"
toc: true
description: "A quickstart guide to creating new content in Lotus Docs"
publishdate: "2023-05-03T22:37:22+01:00"
tags: ["Beginners"]

---
## Free register account
register url  [AiTrados](https://m.aitrados.com/) to get api secret
## Download AiTrados CLient
Windows x86_64 [download](https://m.aitrados.com/download/strategy_client_link/windows/x86_64/)

Linux(ubuntu,debian[.deb]) x86_64 [download](https://m.aitrados.com/download/strategy_client_link/linux/x86_64/debian/)

Or github to [download](https://github.com/aitrados)

## Install AiTrados Client


{{< tabs tabTotal="1">}}
{{% tab tabName="Linux" %}}

```shell
sudo apt install ./aitrados_new_version_debian_linux_amd64.deb
```


{{% /tab %}}
{{< /tabs >}}

### init account in aitrados client
copy  login code on member center

```shell
aitrados init -h https://m.aitrados.com/********************************* -k *********************************
```

if you start aitrados client  with GUI. plese enter login page and input  login code


### Start AiTrados Client
#### Start with cli
```shell
aitrados runserver
```
#### Start with GUI
```shell
aitrados #or Click the Start icon 
```
Or Click the Start icon 

