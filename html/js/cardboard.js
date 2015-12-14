

var cameraMesh = null;
var camera = null;
var canvas = null;


function Cardboard(domVideo)
{

var scene, renderer, element, container, effect, context;

init();

function init()
{
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(
                 90,
                 1.33333,
                 0.001,
                 700);

    camera.position.set(0, 15, 0);
    scene.add(camera);

    renderer = new THREE.WebGLRenderer();

    element = renderer.domElement;

    container = document.getElementById('cardboardContainer');
    container.appendChild(element);

    effect = new THREE.StereoEffect(renderer);



var HMD = (options && options.HMD) ? options.HMD: {
        // Parameters from the Oculus Rift DK1
        hResolution: 1280,
        vResolution: 800,
        hScreenSize: 0.200,
        vScreenSize: 0.0936,
        interpupillaryDistance: 0.064,
        lensSeparationDistance: 0.064,
        eyeToScreenDistance: 0.041,
        distortionK : [1.0, 0.22, 0.24, 0.0],
        chromaAbParameter: [ 0.996, -0.004, 1.014, 0.0]
    };

var options = {
    HMD: HMD
};

    //effect = new THREE.OculusRiftEffect(renderer, options);

    element.addEventListener('click', fullscreen, false);

    // Have to make sure this is a power of 2 or THREE can't work with it.
    canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
    canvas.width = 1024;
    canvas.height = 1024;
//    canvas.width = nextPowerOf2(canvas.width);
//    canvas.height = nextPowerOf2(canvas.height);

    function nextPowerOf2(x) { 
        return Math.pow(2, Math.ceil(Math.log(x) / Math.log(2)));
    }

    context = canvas.getContext('2d');
    texture = new THREE.Texture(canvas);
    texture.context = context;

    var cameraPlane = new THREE.PlaneGeometry(canvas.width, canvas.height);

    cameraMesh = new THREE.Mesh(cameraPlane, new THREE.MeshBasicMaterial({
        color: 0xffffff, opacity: 1, map: texture
    }));
    cameraMesh.position.z = -250;
    cameraMesh.position.y = 50;
    cameraMesh.position.z = -700;
    cameraMesh.position.y = 100;

    scene.add(cameraMesh);

    animate();
}




function animate()
{
//    context.drawImage(piImage, 0, 0, canvas.width, canvas.height);
//    texture.needsUpdate = true;

    //context.drawImage(domVideo, 0, 0);



// we're stretching a 640x480 image over a square.  The distortion sucks.
// Can we instead only use some of the square and best-fit-center the image?
// (and take care when the video res changes)

var coords = MapOntoPreservingRatio(
                 {
                    upperLeft: { x: 0, y: 0 },
                    lowerRight: {
                        x: domVideo.videoWidth,
                        y: domVideo.videoHeight
                    }
                 },
                 {
                    upperLeft: { x: 0, y: 0 },
                    lowerRight: {
                        x: canvas.width,
                        y: canvas.height
                    }
                 }
             );

    context.drawImage(domVideo, 0, 0, domVideo.videoWidth, domVideo.videoHeight, coords.upperLeft.x, coords.upperLeft.y, coords.lowerRight.x, coords.lowerRight.y);

    //context.drawImage(domVideo, 0, 0, domVideo.videoWidth, domVideo.videoHeight, 0, 0, canvas.width, canvas.height);
    texture.needsUpdate = true;

    requestAnimationFrame(animate);

    update();
    render();
}


function resize()
{
    var width = container.offsetWidth;
    var height = container.offsetHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();

    renderer.setSize(width, height);

    effect.setSize(width, height);
}

function update(dt)
{
    resize();
    camera.updateProjectionMatrix();
}

function render(dt)
{
    effect.render(scene, camera);
}

function fullscreen()
{
    if (container.requestFullscreen) {
        container.requestFullscreen();
    } else if (container.msRequestFullscreen) {
        container.msRequestFullscreen();
    } else if (container.mozRequestFullScreen) {
        container.mozRequestFullScreen();
    } else if (container.webkitRequestFullscreen) {
        container.webkitRequestFullscreen();
    }
}



}


