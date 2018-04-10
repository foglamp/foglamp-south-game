BEGIN 	{
		printf("Car   |  Red  | Green | Blue  | Acceleration | Cornering G | Flip Penalty | Total\n");
		printf("------+-------+-------+-------+--------------+-------------+--------------+----------\n");
	}
	{
		printf("%5s | %5d | %5d | %5d |      %7.1f |     %7.1f |       %6d | %.1f\n", $1, $2, $3, $4, $5, $6, $7, $8);
	}
