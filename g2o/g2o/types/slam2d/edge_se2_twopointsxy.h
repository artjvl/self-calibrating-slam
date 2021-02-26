// g2o - General Graph Optimization
// Copyright (C) 2011 R. Kuemmerle, G. Grisetti, H. Strasdat, W. Burgard
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
// * Redistributions of source code must retain the above copyright notice,
//   this list of conditions and the following disclaimer.
// * Redistributions in binary form must reproduce the above copyright
//   notice, this list of conditions and the following disclaimer in the
//   documentation and/or other materials provided with the distribution.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
// IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
// TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
// PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
// TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#ifndef G2O_EDGE_SE2_TWOPOINTS_XY_H
#define G2O_EDGE_SE2_TWOPOINTS_XY_H

#include "g2o/config.h"
#include "g2o_types_slam2d_api.h"
#include "g2o/core/base_variable_sized_edge.h"
#include "vertex_se2.h"
#include "vertex_point_xy.h"

namespace g2o{

  class G2O_TYPES_SLAM2D_API EdgeSE2TwoPointsXY : public BaseVariableSizedEdge<4, Vector4>
  {
    public:
      EIGEN_MAKE_ALIGNED_OPERATOR_NEW;
      EdgeSE2TwoPointsXY();

      virtual void computeError();

      virtual bool read(std::istream& is);
      virtual bool write(std::ostream& os) const;

      virtual bool setMeasurementFromState();

      virtual void initialEstimate(const OptimizableGraph::VertexSet&, OptimizableGraph::Vertex*);
      virtual number_t initialEstimatePossible(const OptimizableGraph::VertexSet&, OptimizableGraph::Vertex*);
  };
}
#endif	// G2O_EDGE_SE2_TWOPOINTS_XY_H
