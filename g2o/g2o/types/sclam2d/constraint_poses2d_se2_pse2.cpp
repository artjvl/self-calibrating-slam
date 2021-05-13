//
// Created by art on 12-04-21.
//

#include "constraint_poses2d_se2_pse2.h"

namespace g2o {

    ConstraintPoses2DSE2PSE2::ConstraintPoses2DSE2PSE2() :
            BaseFixedSizedEdge<3, SE2, NodeSE2, NodeSE2, ParamSE2>()
    {
    }

    void ConstraintPoses2DSE2PSE2::initialEstimate(const OptimizableGraph::VertexSet& from, OptimizableGraph::Vertex* to) {
        (void) to;
        NodeSE2* vi = static_cast<NodeSE2*>(_vertices[0]);
        NodeSE2* vj = static_cast<NodeSE2*>(_vertices[1]);
        ParamSE2* l = static_cast<ParamSE2*>(_vertices[2]);
        if (from.count(l) == 0)
            return;
        if (from.count(vi) == 1) {
            vj->setEstimate(vi->estimate() * l->estimate() * measurement() * l->estimate().inverse());
        } else {
            vi->setEstimate(vj->estimate() * l->estimate() * _inverseMeasurement * l->estimate().inverse());
        }
    }

    bool ConstraintPoses2DSE2PSE2::read(std::istream& is) {
        Vector3 p;
        internal::readVector(is, p);
        _measurement.fromVector(p);
        _inverseMeasurement=measurement().inverse();
        return readInformationMatrix(is);
    }

    bool ConstraintPoses2DSE2PSE2::write(std::ostream& os) const {
        internal::writeVector(os, measurement().toVector());
        return writeInformationMatrix(os);
    }

} // end namespace
