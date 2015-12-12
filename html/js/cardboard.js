

function Cardboard(domVideo)
{

var scene, camera, renderer, element, container, effect, canvas, context;

init();

function init()
{
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(
                 90,
                 1,
                 0.001,
                 700);

    camera.position.set(0, 15, 0);
    scene.add(camera);

    renderer = new THREE.WebGLRenderer();

    element = renderer.domElement;

    container = document.getElementById('cardboardContainer');
    container.appendChild(element);

    effect = new THREE.StereoEffect(renderer);

    element.addEventListener('click', fullscreen, false);

    canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 512;
//    canvas.width = nextPowerOf2(canvas.width);
//    canvas.height = nextPowerOf2(canvas.height);

    function nextPowerOf2(x) { 
        return Math.pow(2, Math.ceil(Math.log(x) / Math.log(2)));
    }

    context = canvas.getContext('2d');
    texture = new THREE.Texture(canvas);
    texture.context = context;

    var cameraPlane = new THREE.PlaneGeometry(512, 512);

    cameraMesh = new THREE.Mesh(cameraPlane, new THREE.MeshBasicMaterial({
        color: 0xffffff, opacity: 1, map: texture
    }));
    cameraMesh.position.z = -200;

    scene.add(cameraMesh);

    animate();
}


function animate()
{
//    context.drawImage(piImage, 0, 0, canvas.width, canvas.height);
//    texture.needsUpdate = true;

    //context.drawImage(domVideo, 0, 0);
    context.drawImage(domVideo, 0, 0, domVideo.videoWidth, domVideo.videoHeight, 0, 0, canvas.width, canvas.height);
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


