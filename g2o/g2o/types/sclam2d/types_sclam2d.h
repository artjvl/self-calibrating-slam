// g2o - General Graph Optimization
// Copyright (C) 2011 R. Kuemmerle, G. Grisetti, W. Burgard
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

#ifndef G2O_TYPES_SCLAM_H
#define G2O_TYPES_SCLAM_H

#include "edge_se2_sensor_calib.h"
#include "vertex_odom_differential_params.h"
#include "edge_se2_odom_differential_calib.h"

#include "node_se2.h"
//#include "node_v1.h"
#include "node_v2.h"
//#include "node_v3.h"

#include "parameter_se2.h"
#include "parameter_v1.h"
#include "parameter_v2.h"
#include "parameter_v3.h"

#include "constraint_pose2d_v2.h"
#include "constraint_poses2d_se2.h"
#include "constraint_poses2d_se2_se2.h"
#include "constraint_poses2d_se2_v1.h"
#include "constraint_poses2d_se2_v2.h"
#include "constraint_poses2d_se2_v3.h"

#include "info3.h"
#include "constraint_info3.h"
#include "constraint_poses2d_se2_i.h"

#endif
