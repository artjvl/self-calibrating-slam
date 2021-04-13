//
// Created by art on 12-04-21.
//

#include "constraint_poses2d_se2_ps2.h"

namespace g2o {
    ConstraintPoses2DSE2PSE2::ConstraintPoses2DSE2PSE2() :
        BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamSE2>() {}
}