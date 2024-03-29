import matplotlib.pyplot as plt

def avg_damage(summary_timestamps, damage_summary):
	average_attack_damage = [] #y axis 1
	average_q_damage = []#y axis 2
	average_w_damage = []#y axis 3
	average_e_damage = []#y axis 4
	average_r_damage = []#y axis 5
	for timestamp in summary_timestamps:
		average_attack = 0
		average_q = 0
		average_w = 0
		average_e = 0
		average_r = 0

		for champion in damage_summary[timestamp]:
			average_attack = average_attack + damage_summary[timestamp][champion]["Attack"]
			average_q = average_q + damage_summary[timestamp][champion]["Q"]["Magic"] + damage_summary[timestamp][champion]["Q"]["Physical"] + damage_summary[timestamp][champion]["Q"]["True"]
			average_w = average_w + damage_summary[timestamp][champion]["W"]["Magic"] + damage_summary[timestamp][champion]["W"]["Physical"] + damage_summary[timestamp][champion]["W"]["True"]
			average_e = average_e + damage_summary[timestamp][champion]["E"]["Magic"] + damage_summary[timestamp][champion]["E"]["Physical"] + damage_summary[timestamp][champion]["E"]["True"]
			average_r = average_r + damage_summary[timestamp][champion]["R"]["Magic"] + damage_summary[timestamp][champion]["R"]["Physical"] + damage_summary[timestamp][champion]["R"]["True"]

		average_attack_damage.insert(len(average_attack_damage), average_attack / 5)
		average_q_damage.insert(len(average_q_damage), average_q / 5)
		average_w_damage.insert(len(average_w_damage), average_w / 5)
		average_e_damage.insert(len(average_e_damage), average_e / 5)
		average_r_damage.insert(len(average_r_damage), average_r / 5)
	
	return average_attack_damage, average_q_damage, average_w_damage, average_e_damage, average_r_damage

def plot_summaries(damage_summary_1, damage_summary_2):
	#match 1
	summary_timestamps_1 = list(damage_summary_1.keys()) #x axis
	summary_timestamps_minutes_1 = [round(int(timestamp) / 60000) for timestamp in summary_timestamps_1 if timestamp != summary_timestamps_1[len(summary_timestamps_1) - 1]]
	summary_timestamps_minutes_1.append(round(int(summary_timestamps_1[len(summary_timestamps_1) - 1]) / 60000) + 1)
	
	average_attack_damage_1, average_q_damage_1, average_w_damage_1, average_e_damage_1, average_r_damage_1 = avg_damage(summary_timestamps_1, damage_summary_1)

	#match 2
	summary_timestamps_2 = list(damage_summary_2.keys()) #x axis
	summary_timestamps_minutes_2 = [round(int(timestamp) / 60000) for timestamp in summary_timestamps_2 if timestamp != summary_timestamps_2[len(summary_timestamps_2) - 1]]
	summary_timestamps_minutes_2.append(round(int(summary_timestamps_2[len(summary_timestamps_2) - 1]) / 60000) + 1)
	
	average_attack_damage_2, average_q_damage_2, average_w_damage_2, average_e_damage_2, average_r_damage_2 = avg_damage(summary_timestamps_2, damage_summary_2)

	fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
	fig.suptitle("Average Damage in Match")

	#plot match 1
	ax1.plot(summary_timestamps_minutes_1, average_attack_damage_1, label="Average Attack Damage")
	ax1.plot(summary_timestamps_minutes_1, average_q_damage_1, label="Average Q Damage")
	ax1.plot(summary_timestamps_minutes_1, average_w_damage_1, label="Average W Damage")
	ax1.plot(summary_timestamps_minutes_1, average_e_damage_1, label="Average E Damage")
	ax1.plot(summary_timestamps_minutes_1, average_r_damage_1, label="Average R Damage")

	y_limit = int(input("y axis limit:\n"))
	ax1.set_ylim(0,y_limit)
	ax1.set_xlim(0,30)

	#plot match 2
	ax2.plot(summary_timestamps_minutes_2, average_attack_damage_2, label="Average Attack Damage")
	ax2.plot(summary_timestamps_minutes_2, average_q_damage_2, label="Average Q Damage")
	ax2.plot(summary_timestamps_minutes_2, average_w_damage_2, label="Average W Damage")
	ax2.plot(summary_timestamps_minutes_2, average_e_damage_2, label="Average E Damage")
	ax2.plot(summary_timestamps_minutes_2, average_r_damage_2, label="Average R Damage")

	ax2.set_ylim(0,y_limit)
	ax2.set_xlim(0,30)

	min_length = min(len(summary_timestamps_minutes_1), len(summary_timestamps_minutes_2))
	attack_difference = []
	for i in range(min_length):
		attack_difference.append(average_attack_damage_2[i] - average_attack_damage_1[i])
	q_difference = []
	for i in range(min_length):
		q_difference.append(average_q_damage_2[i] - average_q_damage_1[i])
	w_difference = []
	for i in range(min_length):
		w_difference.append(average_w_damage_2[i] - average_w_damage_1[i])
	e_difference = []
	for i in range(min_length):
		e_difference.append(average_e_damage_2[i] - average_e_damage_1[i])
	r_difference = []
	for i in range(min_length):
		r_difference.append(average_r_damage_2[i] - average_r_damage_1[i])

	y_axis = []
	for i in range(min_length):
		y_axis.append(summary_timestamps_minutes_1[i])

	ax3.plot(y_axis, attack_difference, label="Attack Damage")
	ax3.plot(y_axis, q_difference, label="Q Damage")
	ax3.plot(y_axis, w_difference, label="W Damage")
	ax3.plot(y_axis, e_difference, label="E Damage")
	ax3.plot(y_axis, r_difference, label="R Damage")

	ax3.set_ylim(-500,500)
	ax3.set_xlim(0,30)

	fig.text(0.5, 0.04, 'Damage', ha='center', va='center')
	fig.text(0.03, 0.5, 'Time (minutes)', ha='center', va='center', rotation='vertical')

	plt.legend(bbox_to_anchor=(1.1, 1.05))
	plt.show()
