/* =============
    Copyright (c) 2026, STMicroelectronics

    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification, are permitted provided that
    the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this list of conditions and the
      following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
      following disclaimer in the documentation and/or other materials provided with the distribution.

    * Neither the name of the copyright holders nor the names of its contributors may be used to endorse or promote
      products derived from this software without specific prior written permission.

    *THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
    INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER / OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
    WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
    USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.*
*/
/**
  **************************************************************************
  * Demo: NanoEdge AI process to include in main program body
  *
  * @note  This program must be completed and customized by the user
  **************************************************************************
  */

/* Includes --------------------------------------------------------------------*/
#include "NanoEdgeAI.h"
/* Private define --------------------------------------------------------------*/
/* Private variables defined by user -------------------------------------------*/
float input_signal[NEAI_INPUT_SIGNAL_LENGTH * NEAI_INPUT_AXIS_NUMBER]; // Buffer of input values
float probabilities[NEAI_NUMBER_OF_CLASSES]; // Buffer of class probabilities
/* Private function prototypes defined by user ---------------------------------*/
/*
 * @brief Collect data process
 *
 * This function is defined by user, depends on applications and sensors
 *
 * @param input_signal: [in, out] buffer of sample values
 * @retval None
 * @note   If NEAI_INPUT_AXIS_NUMBER = 3 (cf NanoEdgeAI.h), the buffer must be
 *         ordered as follow:
 *         [x0 y0 z0 x1 y1 z1 ... xn yn zn], where xi, yi and zi
 *         are the values for x, y and z axes, n is equal to
 *         NEAI_INPUT_SIGNAL_LENGTH (cf NanoEdgeAI.h)
 */
void fill_buffer(float *input_signal)
{
	/* USER BEGIN */
	/* USER END */
}
/* -----------------------------------------------------------------------------*/
int main(void)
{
	/* Initialization ------------------------------------------------------------*/
	enum neai_state error_code = neai_classification_init();
	if (error_code != NEAI_OK) {
		/* Check the returned error code (cf NanoEdgeAI.h). */
	}

	/* Classification ------------------------------------------------------------*/
	int id_class = 0;
	while (1) {
		fill_buffer(input_signal);
		neai_classification(input_signal, probabilities, &id_class);
		/* USER BEGIN */
		/*
		* e.g.: Trigger functions depending on id_class
		* (print output class probabilities using probabilities[id_class],
		* print the name of the associated class using the getter function defined 
		* in NanoEdgeAI.h, neai_get_class_name(id_class),
		* blink LED, ring alarm, etc.).
		*/
		/* USER END */
	}
}
