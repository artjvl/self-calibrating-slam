//
// Created by art on 18-06-21.
//

#include "constraint_poses2d_se2_i.h"

namespace g2o {
    ConstraintPoses2DSE2I::ConstraintPoses2DSE2I() :
        BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, Info3>() {
        _information.setIdentity();
    }

    bool ConstraintPoses2DSE2I::read(std::istream &is) {
        Vector3 p;
        bool state = internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement = measurement().inverse();
        return state;
    }

    bool ConstraintPoses2DSE2I::write(std::ostream &os) const {
        return internal::writeVector(os, measurement().toVector());
    }
}