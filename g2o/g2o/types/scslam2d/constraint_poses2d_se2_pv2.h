//
// Created by art on 23-03-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_PV2_H
#define G2O_CONSTRAINT_POSES2D_SE2_PV2_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "utility_poses2d.h"
#include "../slam2d/se2.h"
#include "node_se2.h"
#include "param_v2.h"

namespace g2o {
    class ConstraintPoses2DSE2PV2 :
        public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamV2> {
    public:
        EIGEN_MAKE_ALIGNED_OPERATOR_NEW
        ConstraintPoses2DSE2PV2();

        const NodeSE2* getNodeSE2(int index) const {
            assert (index >= 0 && index < 2);
            return dynamic_cast<const NodeSE2*>(_vertices[index]);
        }

        ParamV2* getParamV2() const {
            return dynamic_cast<ParamV2 *>(_vertices[2]);
        }

        void computeError() override {
            const SE2 pose_1 = getNodeSE2(0)->estimate();
            const SE2 pose_2 = getNodeSE2(1)->estimate();
            const ParamV2* node_param = getParamV2();
            const Vector2& param = node_param->estimate();

            const SE2 delta = utility2d::computePoseDelta(pose_1, pose_2);

            if (node_param->getType() == "SCALE") {
                const SE2 scaled_delta = utility2d::scale(delta, param);
                _error = utility2d::computePoseDelta(_measurement, scaled_delta).toVector();
            }
        }

        bool read(std::istream& is) override;
        bool write(std::ostream& os) const override;
    };
}

#endif //G2O_CONSTRAINT_POSES2D_SE2_PV2_H
