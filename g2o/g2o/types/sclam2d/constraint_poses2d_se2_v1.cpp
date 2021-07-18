//
// Created by art on 17-07-21.
//

#include "constraint_poses2d_se2_v1.h"

namespace g2o {
    ConstraintPoses2DSE2V1::ConstraintPoses2DSE2V1() :
            BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParameterV1>() {
    }
    bool ConstraintPoses2DSE2V1::read(std::istream& is) {
        Vector3 p;
        internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement = measurement().inverse();
        return readInformationMatrix(is);
    }
    bool ConstraintPoses2DSE2V1::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }
}