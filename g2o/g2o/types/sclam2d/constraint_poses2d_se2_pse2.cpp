//
// Created by art on 12-04-21.
//

#include "constraint_poses2d_se2_pse2.h"

namespace g2o {
    ConstraintPoses2DSE2PSE2::ConstraintPoses2DSE2PSE2() :
        BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamSE2>() {}

    bool ConstraintPoses2DSE2PSE2::read(std::istream& is) {
        Vector3 p;
        std::cout << is.rdbuf() << std::endl;
        internal::readVector(is, p);
        setMeasurement(SE2(p));
//        _inverseMeasurement = measurement().inverse();
        readInformationMatrix(is);
        return is.good() || is.eof();
    }

    bool ConstraintPoses2DSE2PSE2::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }
}