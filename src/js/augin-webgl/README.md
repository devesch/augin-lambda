# augin-webgl

## Description

augin-webgl is a 3D viewer for projects with the .aug file extension with optimizations to open in the browser in an optimized and fast way


## Installation

Soon


## Getting started

```
import { auginComponent } from './augin-webgl/auginComponent.js';

const params = new URLSearchParams(window.location.search)
let url = params.has('aug') ? params.get('aug') : 'file/aug';

const component = new auginComponent();
component.load(url);
```

## Usage

### Load the .aug file

```
load(url: string, id: string, onLoadEvent: EventListener, onProgressEvent: EventListener(progressType: string, progress: number));

progressType = 'download', 'load';
```

Example:

```
let url = 'https://site.com/file.zip';
let id = 'random_chars';
const component = new auginComponent();
component.load(
    url,
    {
        id: id,
        onLoadedEvent: () => {
            console.log("Finish load!");
        },
        onProgressEvent: (event) => {
            if (event.progressType === "download") {
                console.log("Download: ", event.progress);
            } else {
                console.log("Load: ", event.progress);
            }
        }
    }
);
```


### Html WebGL canvas

```
getCanvas() : HTMLElement;
```


### Add event when a object is selected

```
addSelectEvent(event: EventListener (guid: string));
```

Example:

```
const component = new auginComponent();
component.addSelectEvent((event) => {
    console.log("Guid:", event.guid);
});
```


### Select a object passing a guid

```
selectObject(guid: string);
```

Example:

```
let guid = '3wziD_A7bDBQa6ZlDHR__d';
const component = new auginComponent();
component.selectObject(guid);
```


### Toggle the visibility to isolation mode

```
toggleIsolation() : boolean;
```


### Toggle measure mode

```
toggleMeasure() : boolean;
```


### Add event when measure has 2 points, returning distance

```
addMeasureDistanceEvent(event: EventListener (distance: number));
```

Example

```
const component = new auginComponent();
component.addMeasureDistanceEvent((event) => {
    console.log("Distance:", event.distance);
});
```


### Change and apply cut on object

```
changeCut(axis: Axis, side: Side, value : number);

Axis = X, Y, Z;
Side = Left, Right;
```

Example

```
const component = new auginComponent();
component.changeCut(Axis.Z, Side.Right, 0.5);
```


### Show/hide the cut planes

```
showCutPlanes (value: boolean);
```


### Show/hide the status bar

```
showStats (value: boolean);
```


## Roadmap


## Authors

Augin