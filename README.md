# Seattle "Link" Light Rail Tracker

This project contains the code for a simple app that controls an RGB LED matrix
(I used [this one](https://www.adafruit.com/product/2278)) to display the arrival
times of the next light rail trains as provided by the
[OneBusAway API](http://developer.onebusaway.org/modules/onebusaway-application-modules/current/api/where/index.html).

## Motivation

The project is inspired by the signs at bus stops that show how long you have to
wait for the next bus to arrive.

![Example Seattle bus stop sign](https://user-images.githubusercontent.com/862937/177436031-d35daca5-8a12-49b8-9715-05ad8776cedf.png)

## Demo

![Photo of front of RGB matrix in action](https://user-images.githubusercontent.com/862937/177436332-d9646713-a323-4cea-8966-9c41cef49c98.png)

https://user-images.githubusercontent.com/862937/177436398-b41cf8ad-9e1f-4e37-9c1e-98171e6f5608.mp4

## Features

### Configuration

All of the controller's settings are tweakable via a
[textproto](https://developers.google.com/protocol-buffers) input configuration.

### Auto-dimming

The display dims to a user-configurable brightness when the sun goes down. (It
uses the [suntime library](https://github.com/SatAgro/suntime) for this.)

## Dependencies

The RGB matrix is driven via a [library provided by Adafruit](https://learn.adafruit.com/32x16-32x32-rgb-led-matrix/library)

The train arrival times are pulled via the [OneBusAway API](http://developer.onebusaway.org/modules/onebusaway-application-modules/current/api/where/index.html)

Sunset times are calculated via the [suntime library.](https://github.com/SatAgro/suntime)
