
function MapValue(range1Val, range1Start, range1End, range2Start, range2End)
{
    var range1Range = range1End - range1Start;
    var valOffsetFromStart = range1Val - range1Start;

    var pctOfRange = valOffsetFromStart / range1Range;

    var range2Range = range2End - range2Start;

    var range2Val = range2Start + (pctOfRange * range2Range);

    return range2Val;
}



//
// takes two parameters:
// - box1 { upperLeft: { x, y }, lowerRight: { x, y } }
// - box2 { upperLeft: { x, y }, lowerRight: { x, y } }
//
// operating on x/y coordinates where the upper left is (0, 0) and increases
// as you go to the lower right.
//
// returns:
// - { upperLeft: { x, y }, lowerRight { x, y } }
//
// indicates where to draw the content of box1 into box2 while:
// - maximizing the use of the second box
// - preserving the ratio of the first box
// - centering the content into box2
//
function MapOntoPreservingRatio(box1, box2)
{
    var retVal = { upperLeft: { x: 0, y: 0 }, lowerRight: { x: 0, y: 0 } };

    // measure the box sizes
    var box1Width  = box1.lowerRight.x - box1.upperLeft.x;
    var box1Height = box1.lowerRight.y - box1.upperLeft.y;

    var box2Width  = box2.lowerRight.x - box2.upperLeft.x;
    var box2Height = box2.lowerRight.y - box2.upperLeft.y;

    // determine their ratios
    var box1Ratio = box1Width / box1Height;
    var box2Ratio = box2Width / box2Height;

    // By comparing ratios, we can know if box1 is proportionally wider or
    // taller than box2.  This tells us how to map.
    //
    // As an example, if box1 is proportionally wider, then once we scale
    // box1's width to match box2, box1's height will be less than box2's.
    //
    // Therefore we know we need to center the height.
    if (box1Ratio > box2Ratio)
    {
        // Set x values.
        // We know we can fit all of box1's width into box2.
        retVal.upperLeft.x  = box2.upperLeft.x;
        retVal.lowerRight.x = box2.lowerRight.x;

        // determine scaling factor
        var scalingFactor = box2Width / box1Width;

        // When box1 is scaled to fit box2, what does box1's height become?
        // We know it is less than box2.
        // Change the height by the same percent that the width changed.
        var box1HeightScaled = scalingFactor * box1Height;

        // Calculate height difference
        var heightDifference = box2Height - box1HeightScaled;
        var verticalOffset = heightDifference / 2;

        // Set y values.
        // The y value should be offset from the top of box2's height by half
        // the difference in box1 and box2's vertical height difference,
        // leading to being centered.
        retVal.upperLeft.y  = box2.upperLeft.y + verticalOffset;
        retVal.lowerRight.y = retVal.upperLeft.y + box1HeightScaled;
    }
    else if (box1Ratio < box2Ratio)
    {
        // Set y values.
        // We know we can fit all of box1's height into box2.
        retVal.upperLeft.y  = box2.upperLeft.y;
        retVal.lowerRight.y = box2.lowerRight.y;

        // determine scaling factor
        var scalingFactor = box2Height / box1Height;

        // When box1 is scaled to fit box2, what does box1's width become?
        // We know it is less than box2.
        // Change the width by the same percent that the height changed.
        var box1WidthScaled = scalingFactor * box1Width;

        // Calculate width difference
        var widthDifference = box2Width - box1WidthScaled;
        var horizontalOffset = widthDifference / 2;

        // Set x values.
        // The x value should be offset from the left of box2's width by half
        // the difference in box1 and box2's horizontal width difference,
        // leading to being centered.
        retVal.upperLeft.x  = box2.upperLeft.x + horizontalOffset;
        retVal.lowerRight.x = retVal.upperLeft.x + box1WidthScaled;
    }
    else // (box1Ratio == box2Ratio)
    {
        retVal = box2;
    }

    return retVal;
}
