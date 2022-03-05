package main

import (
	"time"

	flowengine "code.trikthom.com/thesis/flow-engine"
	"code.trikthom.com/thesis/flow-engine/actions"
	"code.trikthom.com/thesis/flow-engine/calculations"
	"code.trikthom.com/thesis/flow-engine/conditions"
	"code.trikthom.com/thesis/flow-engine/data"
	"code.trikthom.com/thesis/flow-engine/window"
)

var (
	// Global vars
	pg_target = &data.Variable{Value: 1500}
	soc_min   = &data.Variable{Value: 10}
	soc_max   = &data.Variable{Value: 90}

	soc = &data.Variable{Value: 10}

	p_battery_max     = &data.Variable{Value: 5000}
	p_battery         = &data.Variable{Value: 0}
	battery_discharge = &data.Variable{Value: 0}
	eb_max            = &data.Variable{Value: 13500}
	eb                = &data.Variable{Value: eb_max.Value * (soc.Value / 100.0)}

	global_p_load = &data.Variable{}
)

var (
	start = "2022-02-23T00:00:00Z"
)

func main() {
	e := flowengine.Engine{
		Windows: 8 * 96,
		Flows: []*flowengine.Flow{
			// flow1(),
			DynamicPeakReductionFlow(),
			ArbitrageChargeFlow(),
			// PVChargeFlow(),
			// PrintFlow(),
		},
	}

	e.Run()
}

func flow1() *flowengine.Flow {
	current_step := &data.Variable{Value: 1}

	return &flowengine.Flow{
		Resolution:    data.RESOLUTION_1M,
		CurrentStep:   current_step,
		CurrentWindow: &data.Variable{Value: 1},
		Window:        &data.Variable{Value: 5},

		Actions: &[]*actions.Action{
			actions.Print(current_step),
		},
	}
}

func PrintFlow() *flowengine.Flow {
	return &flowengine.Flow{
		Resolution:    data.RESOLUTION_24H,
		CurrentStep:   &data.Variable{Value: 1},
		CurrentWindow: &data.Variable{Value: 1},
		Window:        &data.Variable{Value: 1},
		Actions:       &[]*actions.Action{},
	}
}

func DynamicPeakReductionFlow() *flowengine.Flow {
	resolution := data.RESOLUTION_1M

	// Window vars
	current_step := &data.Variable{Value: 1}
	current_window := &data.Variable{Value: 1}
	w := &data.Variable{Value: 15}
	wx := &window.Context{Valid: true}

	begin, _ := time.Parse("2006-01-02T15:04:05Z", start)

	wh := data.GetWindowedHistory(&data.History{
		Resolution:  resolution,
		Points:      map[time.Time]*data.Variable{},
		Time:        begin,
		Measurement: "TotalPower",
	}, current_window, w, wx)

	// Local Flow Variables
	p_load_initial := &data.Variable{}
	p_load := &data.Variable{}
	pg_limit := &data.Variable{Value: pg_target.Value}

	// Temp Flow Variables
	ans1 := &data.Variable{}
	ans2 := &data.Variable{}
	ans3 := &data.Variable{}
	ans4 := &data.Variable{}
	ans5 := &data.Variable{}
	ans6 := &data.Variable{}
	w_index := &data.Variable{}
	p_load_avg15 := &data.Variable{}

	return &flowengine.Flow{
		Resolution:    resolution,
		CurrentStep:   current_step,
		CurrentWindow: current_window,
		Window:        w,
		Wx:            wx,

		Actions: &[]*actions.Action{
			actions.GetWindowedMetric(wh, current_step, p_load_initial),
			actions.GetWindowedMetric(wh, current_step, p_load),
			actions.Reset(ans6),

			actions.IfElse(conditions.GreaterThan(p_load, pg_limit), []*actions.Action{
				actions.IfElse(conditions.GreaterThan(soc, soc_min), []*actions.Action{
					actions.FakeSetWindowedMetric(wh, current_step, pg_limit),
				}, []*actions.Action{}),
			}, []*actions.Action{}),

			actions.Calculate(
				calculations.Subtract(current_step, &data.Variable{Value: 1}, ans1),
				calculations.Subtract(w, ans1, ans2),
				calculations.Multiply(pg_target, w, ans3),
				calculations.CumulativeSum(current_step, &data.Variable{Value: 1}, wh, ans4),
				calculations.Subtract(ans3, ans4, ans5),
				calculations.Divide(ans5, ans2, pg_limit),
			),

			actions.IfElse(conditions.GreaterThan(&data.Variable{Value: 0}, pg_limit), []*actions.Action{
				actions.Reset(pg_limit),
			}, []*actions.Action{}),

			actions.IfElse(conditions.GreaterThan(p_load_initial, pg_limit), []*actions.Action{
				actions.IfElse(conditions.GreaterThan(soc, soc_min), []*actions.Action{
					actions.Calculate(
						calculations.Subtract(p_load_initial, pg_limit, ans6),
					),
					actions.IfElse(conditions.GreaterThan(p_battery_max, ans6), []*actions.Action{
						actions.Calculate(
							calculations.Subtract(p_load_initial, pg_limit, p_battery),
							calculations.Multiply(p_battery, &data.Variable{Value: 1 / 60.0}, battery_discharge),
							calculations.Subtract(eb, battery_discharge, eb),
							calculations.Divide(eb, eb_max, soc),
							calculations.Multiply(soc, &data.Variable{Value: 100}, soc),
						),
					}, []*actions.Action{}),
				}, []*actions.Action{}),
			}, []*actions.Action{}),

			actions.GetWindowedMetric(wh, current_step, p_load),

			actions.Calculate(
				calculations.Subtract(w, &data.Variable{Value: 1}, w_index),
			),

			actions.IfElse(conditions.GreaterThan(current_step, w_index), []*actions.Action{
				actions.Calculate(
					calculations.CumulativeSum(w, &data.Variable{Value: 1}, wh, p_load_avg15),
					calculations.Divide(p_load_avg15, w, p_load_avg15),
				),
				actions.IfElse(conditions.GreaterThan(p_load_avg15, pg_target), []*actions.Action{
					actions.Set(pg_target, p_load_avg15),
				}, []*actions.Action{}),
				actions.Save(map[string]*data.Variable{
					"p_load_avg15": p_load_avg15,
				}, &p_load.Time, "multi-flow-peak-reduction"),
			}, []*actions.Action{}),

			actions.Set(global_p_load, p_load),

			actions.Save(map[string]*data.Variable{
				"p_load":            p_load,
				"soc":               soc,
				"eb":                eb,
				"pg_target":         pg_target,
				"pg_limit":          pg_limit,
				"p_load_initial":    p_load_initial,
				"battery_discharge": ans6,
			}, &p_load.Time, "multi-flow-peak-reduction"),
		},
	}
}

func ArbitrageChargeFlow() *flowengine.Flow {
	resolution := data.RESOLUTION_1M

	current_step := &data.Variable{Value: 1}
	current_window := &data.Variable{Value: 1}
	w := &data.Variable{Value: 15}
	// w := &data.Variable{Value: 60 * 24}
	wx := &window.Context{Valid: true}

	begin, _ := time.Parse("2006-01-02T15:04:05Z", start)

	wh_solar := data.GetWindowedHistory(&data.History{
		Resolution:  resolution,
		Points:      map[time.Time]*data.Variable{},
		Time:        begin,
		Measurement: "Solarpower",
	}, current_window, w, wx)

	wh_load := data.GetWindowedHistory(&data.History{
		Resolution:  resolution,
		Points:      map[time.Time]*data.Variable{},
		Time:        begin,
		Measurement: "TotalPower",
	}, current_window, w, wx)

	p_solar := &data.Variable{}
	p_load := &data.Variable{}
	p_charge := &data.Variable{}
	p_grid_import := &data.Variable{}
	p_grid_export := &data.Variable{}

	ans1 := &data.Variable{}
	// ans3 := &data.Variable{}
	return &flowengine.Flow{
		Resolution:    resolution,
		CurrentStep:   current_step,
		CurrentWindow: current_window,
		Window:        w,
		Wx:            wx,

		Actions: &[]*actions.Action{
			actions.Reset(p_charge),
			actions.Reset(p_grid_import),
			actions.Reset(p_grid_export),

			actions.GetWindowedMetric(wh_solar, current_step, p_solar),
			actions.GetWindowedMetric(wh_load, current_step, p_load),

			// temp
			actions.Set(p_load, global_p_load),

			actions.IfElse(conditions.GreaterThan(p_solar, p_load), []*actions.Action{
				actions.IfElse(conditions.GreaterThan(soc, soc_max), []*actions.Action{
					// battery full
					actions.Calculate(
						calculations.Subtract(p_solar, p_charge, p_grid_export),
						calculations.Multiply(p_grid_export, &data.Variable{Value: -1}, p_grid_export),
					),
				}, []*actions.Action{
					actions.Calculate(
						calculations.Subtract(p_solar, p_load, ans1),
					),
					actions.IfElse(conditions.GreaterThan(ans1, p_battery_max), []*actions.Action{
						actions.Set(p_charge, p_battery_max),
					}, []*actions.Action{
						actions.Set(p_charge, ans1),
					}),

					// @todo soc next ipv soc
					actions.IfElse(conditions.GreaterThan(soc, soc_max), []*actions.Action{
						// battery full
					}, []*actions.Action{
						// charge
						actions.Calculate(

							calculations.Divide(p_charge, &data.Variable{Value: 60.0}, p_charge),
							calculations.Add(eb, p_charge, eb),
							calculations.Divide(eb, eb_max, soc),
							calculations.Multiply(soc, &data.Variable{Value: 100}, soc),
							calculations.Multiply(p_charge, &data.Variable{Value: 60.0}, p_charge),
						),
					}),
				}),
			}, []*actions.Action{
				// false - discharge
				actions.IfElse(conditions.GreaterThan(p_load, p_battery_max), []*actions.Action{
					// rechts
					actions.IfElse(conditions.GreaterThan(soc, soc_min), []*actions.Action{
						actions.Set(p_charge, p_battery_max),
						actions.Calculate(calculations.Subtract(p_load, p_charge, p_grid_import)),
					}, []*actions.Action{
						// battery empty
						actions.Calculate(calculations.Subtract(p_load, p_solar, p_grid_import)),
					}),
				}, []*actions.Action{
					// @todo soc next ipv soc
					actions.IfElse(conditions.GreaterThan(soc, soc_min), []*actions.Action{
						actions.Calculate(calculations.Subtract(p_load, p_solar, p_charge)),
					}, []*actions.Action{
						// battery empty
						actions.Calculate(calculations.Subtract(p_load, p_solar, p_grid_import)),
					}),
				}),

				actions.Calculate(
					calculations.Divide(p_charge, &data.Variable{Value: -60.0}, p_charge),
					calculations.Add(eb, p_charge, eb),
					calculations.Divide(eb, eb_max, soc),
					calculations.Multiply(soc, &data.Variable{Value: 100}, soc),
					calculations.Multiply(p_charge, &data.Variable{Value: 60.0}, p_charge),
				),
			}),

			actions.Set(global_p_load, p_load),

			actions.Save(map[string]*data.Variable{
				"p_solar":       p_solar,
				"p_load":        p_load,
				"eb":            eb,
				"p_charge":      p_charge,
				"soc":           soc,
				"p_grid_import": p_grid_import,
				"p_grid_export": p_grid_export,
			}, &p_solar.Time, "multi-flow-arbitrage-charge"),
		},
	}
}

func PVChargeFlow() *flowengine.Flow {
	return &flowengine.Flow{}
}