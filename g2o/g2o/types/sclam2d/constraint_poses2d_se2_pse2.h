//
// Created by art on 12-04-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_PS2_H
#define G2O_CONSTRAINT_POSES2D_SE2_PS2_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "g2o/types/slam2d/se2.h"
#include "node_se2.h"
#include "param_se2.h"

namespace g2o {
    class ConstraintPoses2DSE2PSE2 : public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamSE2> {
    public:
        ConstraintPoses2DSE2PSE2();
        void computeError() {
            const NodeSE2* v1 = static_cast<const NodeSE2*>(_vertices[0]);
            const NodeSE2* v2 = static_cast<const NodeSE2*>(_vertices[1]);
            const ParamSE2* p = static_cast<const ParamSE2*>(_vertices[2]);


            const SE2 delta = v1->estimate().inverse() * v2->estimate();
            const SE2 estimate = p->composeTransformation(delta, true);
            _error = (measurement().inverse() * estimate).toVector();
        }
    };
}

#endif //G2O_CONSTRAINT_POSES2D_SE2_PS2_H
