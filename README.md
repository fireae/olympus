![Alt Olympyus](olympus_logo.png "Olympus")
<h1 align="center">Create a REST API for any ML model, in seconds.</h1>
<h3>WARNING: Currently in beta</h3>

## Guide

- [What is this?](#what-is-this)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [How's this different from Tensorflow Serving?](#hows-this-different-from-tensorflow-serving)
- [Supported ML frameworks](#supported-ml-frameworks)
- [Contributions](#contributions)

### What is this?
<img align="right" src="https://memegenerator.net/img/instances/500x/59976708/deep-learning-deep-learning-everywhere.jpg">

Olympus is basically a command-line tool that you can use to deploy any pre-trained ML/deep learning model as a REST api, in seconds.

I built this tool after becoming tired of manually creating REST apis for a bunch of deep learning models that I was playing with, usually for using them in a web or mobile app.

So if you'd like to quickly deploy that cool deep learning model that you've been tinkering on lately as a REST API, then this tool is for you.

### Installation
`pip install olympus`

### Usage
#### Deploying your model
<img src="./olympus_deploy_usage.gif">

#### Using your model's REST API
<img src="./olympus_preds_usage.gif">

### Features
- Deploys any model with pretrained weights as a REST api, instantly.
- Supports saving and deleting any model you deploy, for quick model management.
- You can activate/deactivate any ML model you've deployed to enable/disable its specific API endpoint

### How's this different from Tensorflow Serving?
As you probably already know, Tensorflow Serving is an open-source, production-grade model deployment tool for deploying Tensorflow models to the cloud.

One of the key differences between Olympus and TF Serving is that, while TF Serving is optimized for the production environment, Olympus is currently more geared towards the development phase. 

For example, when you're building an ML model that needs to be deployed as a REST API so that it can be accessed from a mobile app you're developing, you could use Olympus to easily manage and deploy your models so that you don't have to setup servers manually.

However, when going to production, you would want to properly export your model and use a tool like TF Serving, which is built from the bottom-up for serving models at scale.

### Supported ML Frameworks

Ideally, we're building Olympus to deploy <i><b>any</b></i> ML model as a REST Api.

For now, we support models built with the frameworks listed below.

Don't see your framework? Don't worry! We're constantly adding integrations for more ML frameworks, and you can even extend Olympus with custom adapters for deploying models built with an unsupported framework (more docs on this soon!).

- [Keras](https://keras.io)

### Contributions
Love this project and got an idea for making it better? 
We'd love your help!

Just send over a PR and we'll go on from there.