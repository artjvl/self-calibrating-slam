//
// Created by art on 23-03-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_PSE2_H
#define G2O_CONSTRAINT_POSES2D_SE2_PSE2_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "../slam2d/se2.h"
#include "node_se2.h"
#include "param_se2.h"
#include "utility_poses2d.h"

namespace g2o {
    class ConstraintPoses2DSE2PSE2 :
        public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamSE2> {
    public:
        EIGEN_MAKE_ALIGNED_OPERATOR_NEW
        ConstraintPoses2DSE2PSE2();

        const NodeSE2* getNodeSE2(int index) const {
            assert (index >= 0 && index < 2);
            return dynamic_cast<const NodeSE2*>(_vertices[index]);
        }

        ParamSE2* getParamSE2() const {
            return dynamic_cast<ParamSE2 *>(_vertices[2]);
        }

        void computeError() override {
            const SE2 pose_1 = getNodeSE2(0)->estimate();
            const SE2 pose_2 = getNodeSE2(1)->estimate();
            const ParamSE2* node_param = getParamSE2();
            const SE2& param = node_param->estimate();

            const SE2 delta = utility2d::computePoseDelta(pose_1, pose_2);

            if (node_param->getType() == "OFFSET") {
                const SE2 offset_delta = utility2d::addOffset(delta, param);
                _error = utility2d::computePoseDelta(_measurement, offset_delta).toVector();
            } else if (node_param->getType() == "BIAS") {
                const SE2 biased_delta = utility2d::addBias(delta, param);
                _error = utility2d::computePoseDelta(_measurement, biased_delta).toVector();
            }
        }

        bool read(std::istream& is) override;
        bool write(std::ostream& os) const override;
    };
}

#endif //G2O_CONSTRAINT_POSES2D_SE2_PSE2_H
