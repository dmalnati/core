

function OrientationHelper(cbOnChange)
{
    var t = this;

    function RadToDeg(rad)
    {
        return (rad / (Math.PI / 2)) * 90;
    }

    function WorldDirectionToDegUpDown(wd)
    {
        var x = wd.x;
        var y = wd.y;
        var z = wd.z;

        var tanOfOA = Math.abs(y) /
                      Math.sqrt(Math.pow(x,2) + Math.pow(z,2));
        var theta   = RadToDeg(Math.atan(tanOfOA));

        var degUpDown = theta;
        if (y < 0)
        {
            degUpDown = -degUpDown;
        }

        return degUpDown;
    }

    function WorldDirectionToDegRotate(wd)
    {
        var x = wd.x;
        var y = wd.y;
        var z = wd.z;

        // calculate 360 degree rotation like a standing human rotating to
        // the right.
        // The plane you are standing on is defined by the x and z axis
        // where the x = and z = 0 is the starting orientation.  Rotating
        // right x decreases and z increases.

        var degRot = 0;
        var theta = 0;

        if (x >= 0 && z >= 0)
        {
            theta = RadToDeg(Math.atan(x / z));
            degRot = 90 - theta;
        }
        else if (x < 0 && z >= 0)
        {
            theta = RadToDeg(Math.atan(Math.abs(x) / z));
            degRot = 90 + theta;
        }
        else if (x < 0 && z < 0)
        {
            theta = RadToDeg(Math.atan(Math.abs(x) / Math.abs(z)));
            degRot = 270 - theta;
        }
        else // (x >= 0 && z < 0)
        {
            theta = RadToDeg(Math.atan(x / Math.abs(z)));
            degRot = 270 + theta;
        }

        return degRot;
    }

    function SetUpThreeInterface()
    {
        var scene  = new THREE.Scene();
        var camera = new THREE.PerspectiveCamera(90, 1, 0.001, 700);

        camera.position.set(0, 10, 0);
        scene.add(camera);

        controls = new THREE.DeviceOrientationControls(camera, true);
        controls.connect();
        controls.update();

        // Set up another handler for orientation change.
        // This time we just want to know a change has happened so we
        // can extract values from THREE, who will also have already
        // received the change.
        window.addEventListener(
            'deviceorientation',
            function() {
                // Update the internals of the controls
                controls.update();
                
                var wd = camera.getWorldDirection();

                var degRotation = WorldDirectionToDegRotate(wd);
                var degUpDown   = WorldDirectionToDegUpDown(wd);

                cbOnChange({
                    degRotation: degRotation,
                    degUpDown  : degUpDown
                });
            },
            false);
    }

    SetUpThreeInterface();
}



