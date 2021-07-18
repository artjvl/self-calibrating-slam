//
// Created by art on 17-07-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_V1_H
#define G2O_CONSTRAINT_POSES2D_SE2_V1_H

#include <string>
#include "g2o/core/base_fixed_sized_edge.h"
#include "g2o/types/slam2d/se2.h"
#include "node_se2.h"
#include "parameter_v1.h"
#include "parameter_util.h"

namespace g2o {
    class ConstraintPoses2DSE2V1 : public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParameterV1> {
    public:
        ConstraintPoses2DSE2V1();
        void computeError() {
            NodeSE2* n1 = static_cast<NodeSE2*>(_vertices[0]);
            NodeSE2* n2 = static_cast<NodeSE2*>(_vertices[1]);
            ParameterV1* p = static_cast<ParameterV1*>(_vertices[2]);

            const SE2& p1 = n1->estimate();
            const SE2& p2 = n2->estimate();
            std::string interpretation = p->interpretation();

            SE2 delta = p1.inverse() * p2;
            SE2 error = _inverseMeasurement * ParameterUtil::transform(interpretation, delta, p->toVector3(), true);
            _error = error.toVector();
        }

        void setMeasurement(const SE2& m){
            _measurement = m;
            _inverseMeasurement = m.inverse();
        }

        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;

    protected:
        SE2 _inverseMeasurement;
    };
}

#endif //G2O_CONSTRAINT_POSES2D_SE2_V1_H
