//
// Created by art on 09-07-21.
//

#ifndef G2O_CONSTRAINT_POSES2D_SE2_BIAS_H
#define G2O_CONSTRAINT_POSES2D_SE2_BIAS_H

#include "g2o/core/base_fixed_sized_edge.h"
#include "g2o/types/slam2d/se2.h"
#include "node_se2.h"
#include "param_bias.h"

namespace g2o {

    class ConstraintPoses2DSE2Bias : public BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamBias> {
    public:
        EIGEN_MAKE_ALIGNED_OPERATOR_NEW;
        ConstraintPoses2DSE2Bias();

        void computeError() {
            const NodeSE2* v1   = static_cast<const NodeSE2*>(_vertices[0]);
            const NodeSE2* v2   = static_cast<const NodeSE2*>(_vertices[1]);
            const ParamBias* p   = static_cast<const ParamBias*>(_vertices[2]);

            const SE2& x1 = v1->estimate();
            const SE2& x2 = v2->estimate();
            const SE2& par = p->estimate();

            SE2 delta = x1.inverse() * x2;
            SE2 error;

            // decomposition: estimate = delta - parameters
            error = _inverseMeasurement * (delta * par.inverse());
            _error = error.toVector();
        }

        void setMeasurement(const SE2& m){
            _measurement = m;
            _inverseMeasurement = m.inverse();
        }

        virtual number_t initialEstimatePossible(const OptimizableGraph::VertexSet& from, OptimizableGraph::Vertex* to)
        {
            if (   from.count(_vertices[2]) == 1 // need the laser offset
                   && ((from.count(_vertices[0]) == 1 && to == _vertices[1]) || ((from.count(_vertices[1]) == 1 && to == _vertices[0])))) {
                return 1.0;
            }
            return -1.0;
        }
        virtual void initialEstimate(const OptimizableGraph::VertexSet& from, OptimizableGraph::Vertex* to);

        virtual bool read(std::istream& is);
        virtual bool write(std::ostream& os) const;

    protected:
        SE2 _inverseMeasurement;
    };

} // end namespace

#endif //G2O_CONSTRAINT_POSES2D_SE2_BIAS_H
