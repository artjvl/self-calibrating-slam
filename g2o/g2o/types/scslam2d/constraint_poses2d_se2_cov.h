//
// Created by art on 23-03-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_COV_H
#define G2O_CONSTRAINT_POSES2D_SE2_COV_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "../slam2d/se2.h"
#include "node_se2.h"
#include "info3.h"
#include "utility_poses2d.h"

namespace g2o {
    class ConstraintPoses2DSE2Cov :
        public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, Info3> {
    public:
        EIGEN_MAKE_ALIGNED_OPERATOR_NEW
        ConstraintPoses2DSE2Cov();

        const NodeSE2* getNodeSE2(int index) const {
            assert (index >= 0 && index < 2);
            return dynamic_cast<const NodeSE2*>(_vertices[index]);
        }

        Info3* getInfo3() const {
            return dynamic_cast<Info3*>(_vertices[2]);
        }

        void computeError() override {
            const SE2 pose_1 = getNodeSE2(0)->estimate();
            const SE2 pose_2 = getNodeSE2(1)->estimate();
            const Info3* node_info = getInfo3();
            const Vector3& info_diagonal = node_info->estimate();

            const SE2 delta = utility2d::computePoseDelta(pose_1, pose_2);

            Vector3 difference = utility2d::computePoseDelta(_measurement, delta).toVector();
            _error = info_diagonal.cwiseSqrt().asDiagonal() * difference;
        }

        bool read(std::istream& is) override;
        bool write(std::ostream& os) const override;
    };
}


#endif //G2O_CONSTRAINT_POSES2D_SE2_COV_H
