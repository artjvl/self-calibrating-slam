//
// Created by art on 18-06-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_I_H
#define G2O_CONSTRAINT_POSES2D_SE2_I_H

#include <cmath>
#include "g2o/core/base_fixed_sized_edge.h"
#include "g2o/types/slam2d/se2.h"
#include "node_se2.h"
#include "info3.h"

namespace g2o {
    class ConstraintPoses2DSE2I : public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, Info3> {
    public:
        ConstraintPoses2DSE2I();

        void computeError() {
            const NodeSE2* node_a = static_cast<const NodeSE2*>(_vertices[0]);
            const NodeSE2* node_b = static_cast<const NodeSE2*>(_vertices[1]);
            const Info3* node_info = static_cast<const Info3*>(_vertices[2]);

            const SE2& pose_a = node_a->estimate();
            const SE2& pose_b = node_b->estimate();
            const Vector3& info_diagonal = node_info->estimate();

            SE2 delta = _inverseMeasurement * (pose_a.inverse() * pose_b);
            Vector3 delta_vector = delta.toVector();
            for (int i = 0; i < 3; i++) {
                _error[i] = sqrt(info_diagonal[i]) * delta_vector[i];
            }
        }

        void setMeasurement(const SE2& m) {
            _measurement = m;
            _inverseMeasurement = m.inverse();
        }

        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;

    protected:
        SE2 _inverseMeasurement;
    };
}


#endif //G2O_CONSTRAINT_POSES2D_SE2_I_H
