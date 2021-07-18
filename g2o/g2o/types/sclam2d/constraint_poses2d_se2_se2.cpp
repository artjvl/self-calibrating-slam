//
// Created by art on 17-07-21.
//

#include "constraint_poses2d_se2_se2.h"

namespace g2o {
    ConstraintPoses2DSE2SE2::ConstraintPoses2DSE2SE2() :
            BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParameterSE2>() {
    }
    bool ConstraintPoses2DSE2SE2::read(std::istream& is) {
        Vector3 p;
        internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement = measurement().inverse();
        return readInformationMatrix(is);
    }
    bool ConstraintPoses2DSE2SE2::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }
}