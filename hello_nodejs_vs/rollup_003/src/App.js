import {
	BoxBufferGeometry,
	Mesh,
	MeshBasicMaterial,
	PerspectiveCamera,
	Scene,
	WebGLRenderer
} from 'three';

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GUI } from 'three/examples/jsm/libs/lil-gui.module.min.js';
import { Creature } from '../src/Creature.mjs';
import { Coordinate } from '../src/Coordinate.mjs';

//let camera, scene, renderer;

class App {

	init() {

		this.camera = new PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 1000 );
		this.camera.position.z = 400;

		this.scene = new Scene();

		const geometry = new BoxBufferGeometry( 200, 200, 200 );
		const material = new MeshBasicMaterial();

		this.mesh = new Mesh( geometry, material );
		this.scene.add( this.mesh );

		this.renderer = new WebGLRenderer( { antialias: true } );
		this.renderer.setPixelRatio( window.devicePixelRatio );
		this.renderer.setSize( window.innerWidth, window.innerHeight );
		document.body.appendChild( this.renderer.domElement );

		window.addEventListener( 'resize', onWindowResize, false );

		const controls = new OrbitControls( this.camera, this.renderer.domElement );

		this.create_Creature();
		this.create_GUI();
		animate();
	}

	create_GUI() {
		
		this.current_shape = { name: 'Box' };
		const shapes = [ 'Box', 'Sphere' ];
		
		this.gui = new GUI();
		const shape_folder = this.gui.addFolder('shape'); 
		const shapeCtrl = shape_folder.add( this.current_shape, 'name' ).options( shapes );
		
		shapeCtrl.onChange( function () {

			window.app.shapeChange();

		} );
		shape_folder.open();
	}

	shapeChange() {
		alert("shape changed to: " + this.current_shape.name);
	}

	create_Creature() {
		const coordinate = new Coordinate(0,0,0);
		this.creature = new Creature(coordinate);
	}

	move_cycle() {
		if (this.creature.coordinate.y<50) {
			this.creature.move_forward(1);
		}
		this.mesh.position.x = this.creature.coordinate.x;
		this.mesh.position.y = this.creature.coordinate.y;
		this.mesh.position.z = this.creature.coordinate.z;
		

	}

}

function onWindowResize() {

	window.app.camera.aspect = window.innerWidth / window.innerHeight;
	window.app.camera.updateProjectionMatrix();

	window.app.renderer.setSize( window.innerWidth, window.innerHeight );

}

function animate() {

	requestAnimationFrame( animate );
	window.app.move_cycle();
	window.app.renderer.render( window.app.scene, window.app.camera );

}

export default App;
