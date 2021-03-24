//
// Created by art on 23-03-21.
//

#include "constraint_poses2d_se2_cov.h"

namespace g2o {
    ConstraintPoses2DSE2Cov::ConstraintPoses2DSE2Cov() :
        BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, Info3>() {

        for (int i = 0; i < information().rows(); ++i) {
            for (int j = i; j < information().cols(); ++j) {
                if (i == j) {
                    information()(i, j) = 1;
                } else {
                    information()(i, j) = 0;
                    information()(j, i) = 0;
                }
            }
        }
    }

    bool ConstraintPoses2DSE2Cov::read(std::istream &is) {

        // read measurement
        Vector3 p;
        internal::readVector(is, p);
        setMeasurement(SE2(p));

        return is.good() || is.eof();
    }

    bool ConstraintPoses2DSE2Cov::write(std::ostream &os) const {

        // write measurement
        return internal::writeVector(os, measurement().toVector());
    }
}